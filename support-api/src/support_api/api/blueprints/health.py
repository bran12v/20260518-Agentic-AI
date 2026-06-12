from flask import Blueprint, current_app

bp = Blueprint("health", __name__)

# Live endpoint
@bp.route("/live", methods=["GET"])
def liveness():
    return { "status": "ok" }

# Ready endpoint
@bp.route("/ready", methods=["GET"])
def readiness():
    from support_api.storage import connect

    try:
        conn = connect(current_app.config["DATABASE_URL"])
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        finally:
            conn.close()
    except Exception as err:
        return {"status": "unready", "error": str(err)}, 503
    
    return {"status": "ok"}
