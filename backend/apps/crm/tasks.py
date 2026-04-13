from celery import shared_task


@shared_task
def ping_crm_job():
    return {"status": "ok", "message": "CRM worker is running."}
