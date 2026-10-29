FROM python:3.13-alpine

# Run as a non-root user
RUN adduser -D -H botuser

WORKDIR /app
COPY --chown=botuser:botuser claim_free_items.py ./

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER botuser

CMD ["python", "claim_free_items.py"]
