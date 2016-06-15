import React from 'react';
import { FormattedMessage, injectIntl } from 'react-intl';
import { connect } from 'react-redux';
import ErrorTryAgain from '../../util/ErrorTryAgain';
import LoadingSpinner from '../../util/LoadingSpinner';
import TopicInfluentialStories from './TopicInfluentialStories';
import { fetchTopicInfluentialStories, sortTopicInfluentialStories } from '../../../actions/topicActions';
import * as fetchConstants from '../../../lib/fetchConstants.js';
import { Grid, Row, Col } from 'react-flexbox-grid/lib';
import FlatButton from 'material-ui/FlatButton';
import messages from '../../../resources/messages';

const localMessages = {
  title: { id: 'topic.influentialStories.title', defaultMessage: 'Influential Stories' },
};

class TopicInfluentialStoriesContainer extends React.Component {
  componentDidMount() {
    const { fetchStatus } = this.props;
    if (fetchStatus !== fetchConstants.FETCH_FAILED) {
      this.refetchData();
    }
  }
  componentWillReceiveProps(nextProps) {
    if ((nextProps.filters !== this.props.filters) ||
        (nextProps.sort !== this.props.sort)) {
      const { topicId, fetchData } = this.props;
      fetchData(topicId, nextProps.filters.snapshotId, nextProps.filters.timespanId, nextProps.sort);
    }
  }
  onChangeSort = (newSort) => {
    const { sortData } = this.props;
    sortData(newSort);
  }
  getStyles() {
    const styles = {
      contentWrapper: {
      },
    };
    return styles;
  }
  refetchData = () => {
    const { fetchData, topicId, filters, sort } = this.props;
    fetchData(topicId, filters.snapshotId, filters.timespanId, sort);
  }
  nextPage = () => {
    const { fetchData, topicId, filters, sort, continuationId } = this.props;
    fetchData(topicId, filters.snapshotId, filters.timespanId, sort, continuationId);
  }
  render() {
    const { fetchStatus, fetchData, stories, sort } = this.props;
    const { formatMessage } = this.props.intl;
    let content = fetchStatus;
    const styles = this.getStyles();
    switch (fetchStatus) {
      case fetchConstants.FETCH_SUCCEEDED:
        content = (
          <div>
            <TopicInfluentialStories stories={stories} onChangeSort={this.onChangeSort} sortedBy={sort} />
            <FlatButton label={formatMessage(messages.nextPage)} primary onClick={this.nextPage} />
          </div>
        );
        break;
      case fetchConstants.FETCH_FAILED:
        content = <ErrorTryAgain onTryAgain={fetchData} />;
        break;
      default:
        content = <LoadingSpinner />;
    }
    return (
      <div style={styles.root}>
        <Grid>
          <Row>
            <Col lg={12}>
              <div style={styles.contentWrapper}>
                <h2><FormattedMessage {...localMessages.title} /></h2>
                {content}
              </div>
            </Col>
          </Row>
        </Grid>
      </div>
    );
  }
}

TopicInfluentialStoriesContainer.ROWS_PER_PAGE = 20;

TopicInfluentialStoriesContainer.propTypes = {
  fetchStatus: React.PropTypes.string.isRequired,
  sort: React.PropTypes.string.isRequired,
  stories: React.PropTypes.array.isRequired,
  params: React.PropTypes.object.isRequired,       // params from router
  topicId: React.PropTypes.number.isRequired,
  topicInfo: React.PropTypes.object.isRequired,
  fetchData: React.PropTypes.func.isRequired,
  sortData: React.PropTypes.func.isRequired,
  intl: React.PropTypes.object.isRequired,
  filters: React.PropTypes.object.isRequired,
  continuationId: React.PropTypes.number,
};

const mapStateToProps = (state) => ({
  fetchStatus: state.topics.selected.stories.fetchStatus,
  sort: state.topics.selected.stories.sort,
  stories: state.topics.selected.stories.stories,
  continuationId: state.topics.selected.stories.continuation_id,
  filters: state.topics.selected.filters,
  topicId: state.topics.selected.id,
  topicInfo: state.topics.selected.info,
});

const mapDispatchToProps = (dispatch) => ({
  fetchData: (topicId, snapshotId, timespanId, sort, continuationId) => {
    if ((snapshotId !== null) && (timespanId !== null)) {
      dispatch(fetchTopicInfluentialStories(topicId, snapshotId, timespanId, sort,
        TopicInfluentialStoriesContainer.ROWS_PER_PAGE, continuationId));
    }
  },
  sortData: (sort) => {
    dispatch(sortTopicInfluentialStories(sort));
  },
});

export default injectIntl(connect(
  mapStateToProps,
  mapDispatchToProps
)(TopicInfluentialStoriesContainer));
