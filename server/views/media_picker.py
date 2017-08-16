import logging
from flask import jsonify, request
import flask_login
from multiprocessing import Pool
from media_search import media_search, _matching_tags_by_set
from server import app
from server.util.request import arguments_required, api_error_handler
from server.auth import user_mediacloud_client, user_has_auth_role, ROLE_MEDIA_EDIT
from server.util.tags import VALID_COLLECTION_TAG_SETS_IDS
from server.views.sources.favorites import add_user_favorite_flag_to_sources, add_user_favorite_flag_to_collections

logger = logging.getLogger(__name__)

MAX_SOURCES = 20
MAX_COLLECTIONS = 20
MEDIA_SEARCH_POOL_SIZE = len(VALID_COLLECTION_TAG_SETS_IDS)

# TODO there are two very similar calls in sources/search.py - string vs arguments passed. may need args so not yet extracting

@app.route('/api/mediapicker/sources/search', methods=['GET'])
@flask_login.login_required
@arguments_required('keyword')
@api_error_handler
def api_mediapicker_source_search():
    tags = None
    search_str = request.args['keyword']
    cleaned_search_str = None if search_str == '*' else search_str
    if 'tags[]' in request.args:
        tags = request.args['tags[]'].split(',')
    if tags is None:
        source_list = media_search(cleaned_search_str)[:MAX_SOURCES]
    else:
        source_list = media_search(cleaned_search_str, tags_id=tags[0])[:MAX_SOURCES]
    add_user_favorite_flag_to_sources(source_list)
    return jsonify({'list':source_list})

@app.route('/api/mediapicker/collections/search', methods=['GET'])
@flask_login.login_required
@arguments_required('keyword')
@api_error_handler
def api_mediapicker_collection_search():
    public_only = False if user_has_auth_role(ROLE_MEDIA_EDIT) else True
    search_str = request.args['keyword']
    results = _matching_tags_by_set(search_str, public_only)
    trimmed = [r[:MAX_COLLECTIONS] for r in results]
    flat_list = [item for sublist in trimmed for item in sublist]
    add_user_favorite_flag_to_collections(flat_list)
    return jsonify({'list': flat_list})