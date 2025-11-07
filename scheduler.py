import schedule
import time
from datetime import datetime
import sys
from wizardry_bot import WizardryBot

def run_bot():
    """Run the bot and log the execution."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"[{timestamp}] Starting scheduled bot run...")
    print(f"{'='*60}\n")

    try:
        bot = WizardryBot('config.json')
        bot.run()
        print(f"\n[{timestamp}] Bot run completed successfully!")
    except Exception as e:
        print(f"\n[{timestamp}] Bot run failed with error: {str(e)}")
        # Don't exit, continue running and wait for next scheduled run

    print(f"\n{'='*60}")
    print(f"Next run scheduled in 7 days")
    print(f"{'='*60}\n")

def main():
    """Main scheduler function."""
    print("="*60)
    print("Wizardry Store Automation Bot - Scheduler Started")
    print("="*60)
    print("Schedule: Every Monday at 10:00 AM")
    print("Waiting for scheduled time...")
    print("="*60 + "\n")

    # Schedule the bot to run every Monday at 10:00 AM
    schedule.every().monday.at("10:00").do(run_bot)

    # Optional: Run immediately on startup (comment out if you don't want this)
    # print("Running bot immediately on startup...\n")
    # run_bot()

    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user.")
        sys.exit(0)
