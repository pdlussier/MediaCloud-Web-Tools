import logging
from flask import jsonify, request
import flask_login
import datetime as dt

from server import app
from server.util.request import api_error_handler, form_fields_required
from server.auth import user_mediacloud_client, user_mediacloud_key
from server.util.pushshift import reddit_submission_normalized_and_split_story_count, reddit_top_submissions, NEWS_SUBREDDITS

logger = logging.getLogger(__name__)

OPEN_WEB = 1

@app.route('/api/topics/platforms/all', methods=['GET'])
@flask_login.login_required
@api_error_handler
def topic_platform_list():
    return jsonify({'results': [{'type': 'open web', 'platform_seed_query': 'dummy'}, {'type': 'reddit', 'platform_seed_query': 'dummy'}, {'type': 'twitter', 'platform_seed_query': 'dummy'}]})



@app.route('/api/topics/<topics_id>/platforms/list', methods=['GET'])
@flask_login.login_required
def get_topic_platforms(topics_id):
    # media_type_tags = tags_in_tag_set(TOOL_API_KEY, TAG_SETS_ID_MEDIA_TYPE)
    # how do we get all the seed queries per topic ?
    #merge what the topic has versus what the topic doens't by adding in the topic_seed_queries_id
    return jsonify({'results': [{'id':56, 'type': 'open web', 'platform_seed_query': 'storytelling'}, {'type': 'reddit', 'platform_seed_query': 'dummy'}, {'type': 'twitter', 'platform_seed_query': 'dummy'}]})

# maybe push this to js, we'll see
@app.route('/api/topics/<topics_id>/platforms/<platform_id>', methods=['GET'])
@flask_login.login_required
def get_platform_by_id(topics_id, platform_id):
    # iterate through topic seed queries array
    return jsonify({'id':56, 'type': 'open web', 'platform_seed_query': 'storytelling'}) #need media_ids


@app.route('/api/topics/<topics_id>/platforms/add', methods=['POST'])
@flask_login.login_required
@api_error_handler
def topic_add_platform(topics_id):
    user_mc = user_mediacloud_client()
    platform = request.form['current_platform_type']
    query = request.form['platform_query']

    source = request.form['source'] if 'source' in request.form else None
    # do we need to add dates?
    result = user_mc.topicAddSeedQuery(topics_id, platform, source, query)
    result['success'] = result['topic_seed_query']['topic_seed_queries_id']
    return jsonify(result) #topic_seed_queries_id


@app.route('/api/topics/<topics_id>/platforms/<platform_id>/update', methods=['POST'])
@flask_login.login_required
@api_error_handler
def topic_update_platform(topics_id, platform_id):
    user_mc = user_mediacloud_client()
    platform = request.form['current_platform_type']
    query = request.form['platform_query']

    source = request.form['source'] if 'source' in request.form else None
    #TODO update or remove/add?
    # remove id, add new, return new id
    result = user_mc.topicUpdateSeedQuery(topics_id, platform_id, source, query)
    result['success'] = result['topic_seed_query']['topic_seed_queries_id']
    return jsonify(result) #topic_seed_queries_id


@app.route('/api/topics/<topics_id>/platforms/remove', methods=['GET'])
@flask_login.login_required
@api_error_handler
def topic_remove_platform(topics_id, platform_id):
    user_mc = user_mediacloud_client()
    query = request.form['platform_query']
    result = user_mc.topicRemoveSeedQuery(topics_id, topic_seed_queries_id = platform_id)
    return jsonify({"results": result})

@app.route('/api/topics/<topics_id>/platforms/preview/stories', methods=['GET'])
@flask_login.login_required
@api_error_handler
def api_topics_platform_preview_story_sample(topics_id):
    user_mc = user_mediacloud_client()

    #will do something conditional depending on platform
    platform = request.args['current_platform_type']
    topic = user_mc.topic(topics_id)
    platform_query = request.args['platform_query']
    num_stories = request.args['limit']

    if platform == 'reddit':
        start_date, end_date = parse_query_dates(topic)
        story_count_result = reddit_top_submissions(query=platform_query,
                                                   start_date=start_date, end_date=end_date,
                                                   subreddits=NEWS_SUBREDDITS)
    else:
        story_count_result = user_mc.storyList(solr_query=platform_query, sort=user_mc.SORT_RANDOM, rows=num_stories)
    return jsonify(story_count_result)


def parse_query_dates(args):

    if 'startDate' in args:
        start_date = dt.datetime.strptime(args['startDate'], "%Y-%m-%d")
    elif 'start_date' in args:
        start_date = dt.datetime.strptime(args['start_date'], "%Y-%m-%d")

    if 'endDate' in args:
        end_date = dt.datetime.strptime(args['endDate'], "%Y-%m-%d")
    elif 'end_date' in args:
        end_date = dt.datetime.strptime(args['end_date'], "%Y-%m-%d")

    return start_date, end_date

@app.route('/api/topics/<topics_id>/platforms/preview/story-count', methods=['GET'])
@flask_login.login_required
@api_error_handler
def api_topics_platform_preview_story_count(topics_id):
    user_mc = user_mediacloud_client()
    #will do something conditional depending on platform
    platform = request.args['current_platform_type']
    platform_query = request.args['platform_query']
    topic = user_mc.topic(topics_id)

    if platform == 'reddit':
        start_date, end_date = parse_query_dates(topic)
        story_count_result = reddit_submission_normalized_and_split_story_count(query=platform_query,
                                                                               start_date = start_date, end_date=end_date,
                                                                               subreddits=NEWS_SUBREDDITS)

    # get inherited topic dates and send them along w
    else:
        story_count_result = user_mc.storyCount(solr_query=platform_query)
    return jsonify(story_count_result)