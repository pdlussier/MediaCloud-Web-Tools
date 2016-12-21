import logging
from flask import jsonify, request
import flask_login
from operator import itemgetter
from mediacloud.tags import MediaTag, TAG_ACTION_ADD, TAG_ACTION_REMOVE

from server import app, mc
from server.util.request import arguments_required, form_fields_required, api_error_handler
from server.cache import cache
from server.auth import user_mediacloud_key, user_mediacloud_client
from server.views.sources.words import cached_wordcount, stream_wordcount_csv
from server.views.sources.geocount import stream_geo_csv, cached_geotag_count
from server.views.sources.sentences import cached_recent_sentence_counts, stream_sentence_count_csv
import server.util.csv as csv
from server.views.sources import COLLECTIONS_TAG_SET_ID

logger = logging.getLogger(__name__)

@app.route('/api/collections/set/<tag_sets_id>', methods=['GET'])
@flask_login.login_required
@api_error_handler
def api_collection_set(tag_sets_id):
    user_mc = user_mediacloud_client()
    info = _cached_public_collection_list(user_mediacloud_key(), tag_sets_id)
    return jsonify(info)

@cache
def _cached_public_collection_list(user_mc_key, tag_sets_id):
    user_mc = user_mediacloud_client()
    tag_set = user_mc.tagSet(tag_sets_id)
    collection_list = user_mc.tagList(tag_sets_id=tag_sets_id, rows=100, public_only=True)
    collection_list = sorted(collection_list, key=itemgetter('label'))
    return {
        'name': tag_set['label'],
        'description': tag_set['description'],
        'collections': collection_list
    }

@app.route('/api/collections/list', methods=['GET'])
@arguments_required('coll[]')
@flask_login.login_required
@api_error_handler
def api_collections_by_ids():
    collIdArray = request.args['coll[]'].split(',')
    sources_list = []
    for tagsId in collIdArray:
        info = {}
        all_media = collection_media_list(user_mediacloud_key(), tagsId)
        info = [{'id':m['media_id'], 'name':m['name'], 'url':m['url']} for m in all_media]
        sources_list += info;
    return jsonify({'results':sources_list})


@app.route('/api/collections/<collection_id>/details')
@flask_login.login_required
@api_error_handler
def api_collection_details(collection_id):
    user_mc = user_mediacloud_client()
    info = user_mc.tag(collection_id)
    info['id'] = collection_id
    info['tag_set'] = _tag_set_info(user_mediacloud_key(), info['tag_sets_id'])
    all_media = collection_media_list(user_mediacloud_key(), collection_id)
    info['media'] = [{'id':m['media_id'], 'name':m['name'], 'url':m['url']} for m in all_media]
    return jsonify({'results':info})

@app.route('/api/collections/<collection_id>/sources.csv')
@flask_login.login_required
@api_error_handler
def api_collection_sources_csv(collection_id):
    user_mc = user_mediacloud_client()
    info = user_mc.tag(collection_id)
    all_media = collection_media_list(user_mediacloud_key(), collection_id)
    props = ['media_id', 'name', 'url']
    filename = info['label']+" - sources.csv"
    return csv.stream_response(all_media, props, filename)

@app.route('/api/collections/<collection_id>/sources/sentences/count')
@flask_login.login_required
@api_error_handler
def collection_source_sentence_counts(collection_id):
    results = _cached_media_with_sentence_counts(user_mediacloud_key(), collection_id)
    return jsonify({'sources': results})

@app.route('/api/collections/<collection_id>/sources/sentences/count.csv')
@flask_login.login_required
@api_error_handler
def collection_source_sentence_counts_csv(collection_id):
    user_mc = user_mediacloud_client()
    info = user_mc.tag(collection_id)
    results = _cached_media_with_sentence_counts(user_mediacloud_key(), collection_id)
    props = ['media_id', 'name', 'url', 'sentence_count', 'sentence_pct']
    filename = info['label']+" - source sentence counts.csv"
    return csv.stream_response(results, props, filename)

@cache
def _cached_media_with_sentence_counts(user_mc_key, tag_sets_id):
    sample_size = 2000
    # list all sources first
    sources_by_id = { c['media_id']:c for c in collection_media_list(user_mediacloud_key(), tag_sets_id)}
    sentences = mc.sentenceList('*', 'tags_id_media:'+str(tag_sets_id), rows=sample_size, sort=mc.SORT_RANDOM)
    # sum the number of sentences per media source
    sentence_counts = { media_id:0 for media_id in sources_by_id.keys() }
    if 'docs' in sentences['response']:
        for sentence in sentences['response']['docs']:
            sentence_counts[sentence['media_id']] = sentence_counts[sentence['media_id']] + 1.
    # add in sentence count info to media info
    for media_id in sentence_counts.keys():
        sources_by_id[media_id]['sentence_count'] = sentence_counts[media_id]
        sources_by_id[media_id]['sentence_pct'] = sentence_counts[media_id] / sample_size
    return sources_by_id.values()

def _tag_set_info(user_mc_key, tag_sets_id):
    user_mc = user_mediacloud_client()
    return user_mc.tagSet(tag_sets_id)

def collection_media_list(user_mc_key, tags_id):
    more_media = True
    all_media = []
    max_media_id = 0
    while more_media:
        logger.debug("last_media_id %d", max_media_id)
        media = collection_media_list_page(user_mc_key, tags_id, max_media_id)
        all_media = all_media + media
        if len(media) > 0:
            max_media_id = media[len(media)-1]['media_id']
        more_media = len(media) != 0
    return sorted(all_media, key=lambda t: t['name'])

def collection_media_list_page(user_mc_key, tags_id, max_media_id):
    '''
    We have to do this on the page, not the full list because memcache has a 1MB cache upper limit,
    and some of the collections have TONS of sources
    '''
    user_mc = user_mediacloud_client()
    return user_mc.mediaList(tags_id=tags_id, last_media_id=max_media_id, rows=100)

@app.route('/api/collections/<collection_id>/sentences/count', methods=['GET'])
@flask_login.login_required
@api_error_handler
def api_collection_sentence_count(collection_id):
    info = {}
    info['sentenceCounts'] = cached_recent_sentence_counts(user_mediacloud_key(), ['tags_id_media:'+str(collection_id)])
    return jsonify({'results':info})

@app.route('/api/collections/<collection_id>/sentences/sentence-count.csv', methods=['GET'])
@flask_login.login_required
@api_error_handler
def collection_sentence_count_csv(collection_id):
    return stream_sentence_count_csv(user_mediacloud_key(), 'sentenceCounts-Collection-' +collection_id, collection_id, "tags_id_media")

@app.route('/api/collections/<collection_id>/geography')
@flask_login.login_required
@api_error_handler
def geo_geography(collection_id):
    info = {}
    info['geography'] = cached_geotag_count(user_mediacloud_key(), 'tags_id_media:'+str(collection_id))
    return jsonify({'results':info})

@app.route('/api/collections/<collection_id>/geography/geography.csv')
@flask_login.login_required
@api_error_handler
def collection_geo_csv(collection_id):
    return stream_geo_csv(user_mediacloud_key(), 'geography-Collection-' + collection_id, collection_id, "tags_id_media")

@app.route('/api/collections/<collection_id>/words')
@flask_login.login_required
@api_error_handler
def collection_words(collection_id):
    info = {
        'wordcounts': cached_wordcount(user_mediacloud_key, 'tags_id_media:'+str(collection_id))
    }
    return jsonify({'results':info})

@app.route('/api/collections/<collection_id>/words/wordcount.csv', methods=['GET'])
@flask_login.login_required
@api_error_handler
def collection_wordcount_csv(collection_id):
    return stream_wordcount_csv(user_mediacloud_key(), 'wordcounts-Collection-' + collection_id, collection_id, "tags_id_media")

@app.route('/api/collections/create', methods=['POST'])
@form_fields_required('name', 'description')
@flask_login.login_required
@api_error_handler
def collection_create():
    user_mc = user_mediacloud_client()
    name = request.form['name']
    description = request.form['description']
    static = request.form['static'] if 'static' in request.form else None
    show_on_stories = request.form['showOnStories'] if 'showOnStories' in request.form else None
    show_on_media = request.form['showOnMedia'] if 'showOnMedia' in request.form else None
    sources = request.form['sources[]'].split(',')
    # first create the collection
    new_collection = user_mc.createTag(COLLECTIONS_TAG_SET_ID, name, name, description, 
        is_static=(static=='true'),
        show_on_stories=(show_on_stories=='true'),
        show_on_media=(show_on_media=='true'))
    # then go through and tag all the sources specified with the new collection id
    tags = [ MediaTag(sid, tags_id=new_collection['tag']['tags_id'], action=TAG_ACTION_ADD) for sid in sources ]
    if len(tags) > 0:
        user_mc.tagMedia(tags)
    return jsonify(new_collection['tag'])

@app.route('/api/collections/<collection_id>/update', methods=['POST'])
@form_fields_required('name', 'description')
@flask_login.login_required
@api_error_handler
def collection_update(collection_id):
    user_mc = user_mediacloud_client()
    name = request.form['name']
    description = request.form['description']
    static = request.form['static'] if 'static' in request.form else None
    show_on_stories = request.form['showOnStories'] if 'showOnStories' in request.form else None
    show_on_media = request.form['showOnMedia'] if 'showOnMedia' in request.form else None
    source_ids = [int(sid) for sid in request.form['sources[]'].split(',')]
    # first update the collection
    updated_collection = user_mc.updateTag(COLLECTIONS_TAG_SET_ID, name, name, description, 
        is_static=(static=='true'),
        show_on_stories=(show_on_stories=='true'),
        show_on_media=(show_on_media=='true'))
    # get the sources in the collection first, then remove and add as needed
    existing_source_ids = [m['media_id'] for m in collection_media_list(user_mediacloud_key(), collection_id)]
    source_ids_to_remove = list(set(existing_source_ids) - set(source_ids))
    source_ids_to_add = [sid for sid in source_ids if sid not in existing_source_ids]
    logger.info(existing_source_ids)
    logger.info(source_ids_to_add)
    logger.info(source_ids_to_remove)
    # then go through and tag all the sources specified with the new collection id
    tags_to_add = [ MediaTag(sid, tags_id=collection_id, action=TAG_ACTION_ADD) for sid in source_ids_to_add ]
    tags_to_remove = [ MediaTag(sid, tags_id=collection_id, action=TAG_ACTION_REMOVE) for sid in source_ids_to_remove ]
    tags = tags_to_add + tags_to_remove
    if len(tags) > 0:
        user_mc.tagMedia(tags)
    return jsonify(updated_collection['tag'])
