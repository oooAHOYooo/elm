from flask import Blueprint, jsonify
from .scraper import get_live_data

bp = Blueprint("change_new_haven_live", __name__)


@bp.route("/api/change-new-haven-live")
def api_change_new_haven_live():
    data = get_live_data()
    return jsonify(data)



