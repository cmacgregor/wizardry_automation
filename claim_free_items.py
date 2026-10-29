"""Claim the weekly free items from the Wizardry Xsolla web shop without a browser.

Logs in with the user ID, lists the store items and claims every free item that
still has a claim available. Set DRY_RUN=true to list what would be claimed
without claiming anything.

Runs once by default. Set CHECK_INTERVAL_HOURS to keep running and check again
every N hours; already-claimed items are skipped, so frequent checks are safe.
"""
import json
import os
import sys
import time
from datetime import datetime
import urllib.error
import urllib.parse
import urllib.request

PROJECT_ID = 261998
MERCHANT_ID = 413457
LOGIN_ID = '43a9093c-fd6b-4674-9f9e-0687cd3bcc61'
WEBHOOK_URL = 'https://app.daphne.wizardry.info/api/v1/vessel/xsolla/webshops/callback'
STORE_ORIGIN = 'https://store.wizardry.info'

LOGIN_URL = 'https://sb-user-id-service.xsolla.com/api/v1/user-id'
STORE_API = f'https://store.xsolla.com/api/v2/project/{PROJECT_ID}'
ITEM_GROUPS = ['flash-sales', 'limited-time-items', 'gems', 'free-items']

HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Origin': STORE_ORIGIN,
    'Referer': f'{STORE_ORIGIN}/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36',
}


def request_json(url, method='GET', body=None, token=None):
    """Send a request and return the decoded JSON response (or None if empty)."""
    headers = dict(HEADERS)
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            raw = res.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors='replace')
        raise RuntimeError(f'{method} {url} failed with HTTP {e.code}: {detail}') from e
    return json.loads(raw) if raw else None


def login(user_id, country):
    """Log in with the user ID and return the store access token."""
    body = {
        'settings': {'projectId': PROJECT_ID, 'merchantId': MERCHANT_ID},
        'loginId': LOGIN_ID,
        'webhookUrl': WEBHOOK_URL,
        'user': {'id': user_id, 'country': country},
        'isUserIdFromWebhook': False,
    }
    token = request_json(LOGIN_URL, method='POST', body=body).get('token')
    if not token:
        raise RuntimeError('Login response did not contain a token')
    return token


def list_items(token):
    """Return every item in the store groups, following pagination."""
    items = []
    offset = 0
    while True:
        query = urllib.parse.urlencode(
            [('external_id[]', group) for group in ITEM_GROUPS]
            + [('locale', 'en'), ('offset', offset), ('limit', 50)]
        )
        page = request_json(f'{STORE_API}/items/virtual_items/group?{query}', token=token)
        items.extend(page.get('items', []))
        if not page.get('has_more'):
            return items
        offset += 50


def claims_available(item):
    """Return how many times this free item can still be claimed."""
    per_user = (item.get('limits') or {}).get('per_user')
    if not per_user:
        return 1  # No per-user limit reported
    return per_user.get('available', 0)


def claim(token, sku):
    """Create a free order for the item, which grants it immediately."""
    sku_path = urllib.parse.quote(sku, safe='')
    return request_json(f'{STORE_API}/free/item/{sku_path}', method='POST', body={}, token=token)


def claim_all(user_id, country, dry_run):
    """Log in and claim every free item that is still available."""
    print('Logging in...')
    token = login(user_id, country)

    free_items = [item for item in list_items(token) if item.get('is_free')]
    if not free_items:
        print('No free items found in the store')
        return

    claimed = 0
    for item in free_items:
        name = f"{item.get('name')} ({item['sku']})"
        if claims_available(item) <= 0:
            print(f'Already claimed: {name}')
            continue
        if dry_run:
            print(f'[DRY RUN] Would claim: {name}')
            continue
        order = claim(token, item['sku'])
        print(f'Claimed: {name} -> {order}')
        claimed += 1

    print(f'Done. Claimed {claimed} item(s).')


def main():
    user_id = os.getenv('USER_ID')
    if not user_id or user_id == 'YOUR_USER_ID_HERE':
        sys.exit('USER_ID environment variable must be set')
    country = os.getenv('COUNTRY', 'US')
    dry_run = os.getenv('DRY_RUN', 'false').lower() in ('true', '1', 'yes')
    interval_hours = float(os.getenv('CHECK_INTERVAL_HOURS') or 0)

    if not interval_hours:
        try:
            claim_all(user_id, country, dry_run)
        except Exception as e:
            sys.exit(f'Claim failed: {e}')
        return

    print(f'Checking for free items every {interval_hours:g} hour(s)')
    while True:
        print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] Checking for free items...")
        try:
            claim_all(user_id, country, dry_run)
        except Exception as e:
            # Keep running; the next check retries
            print(f'Claim failed: {e}')
        time.sleep(interval_hours * 3600)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
