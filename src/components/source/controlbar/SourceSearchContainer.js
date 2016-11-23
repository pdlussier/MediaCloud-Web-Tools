import React from 'react';
import { injectIntl } from 'react-intl';
import { connect } from 'react-redux';
import AutoComplete from 'material-ui/AutoComplete';
import MenuItem from 'material-ui/MenuItem';
import { fetchSourceSearch, fetchCollectionSearch } from '../../../actions/sourceActions';

const MAX_SUGGESTION_CHARS = 40;

class SourceSearchContainer extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      lastSearchString: '',
    };
  }

  handleClick = (item) => {
    const { onMediaSourceSelected, onCollectionSelected } = this.props;
    if (item.type === 'mediaSource') {
      if (onMediaSourceSelected) onMediaSourceSelected(item);
    } else if (item.type === 'collection') {
      if (onCollectionSelected) onCollectionSelected(item);
    }
  }

  shouldFireSearch = (newSearchString) => {
    if ((newSearchString.length > 0) &&
        (newSearchString !== this.state.lastSearchString) &&
        Math.abs(newSearchString.length - this.state.lastSearchString.length) > 2) {
      this.setState({ lastSearchString: newSearchString });
      return true;
    }
    return false;
  }

  handleUpdateInput = (searchString) => {
    const { search } = this.props;
    if (this.shouldFireSearch(searchString)) {
      search(searchString);
    }
  }

  render() {
    const { sourceResults, collectionResults } = this.props;
    const results = sourceResults.concat(collectionResults);
    const resultsAsComponents = results.map(item => ({
      text: item.name,
      value: (
        <MenuItem
          onClick={() => this.handleClick(item)}
          primaryText={(item.name.length > MAX_SUGGESTION_CHARS) ? `${item.name.substr(0, MAX_SUGGESTION_CHARS)}...` : item.name}
        />
      ),
    }));
    return (
      <div className="source-search">
        <AutoComplete
          hintText="search for media by name or URL"
          fullWidth
          openOnFocus
          dataSource={resultsAsComponents}
          onUpdateInput={this.handleUpdateInput}
          maxSearchResults={10}
          filter={() => true}
        />
      </div>
    );
  }

}

SourceSearchContainer.propTypes = {
  intl: React.PropTypes.object.isRequired,
  // from parent
  searchSources: React.PropTypes.bool,
  searchCollections: React.PropTypes.bool,
  onMediaSourceSelected: React.PropTypes.func,
  onCollectionSelected: React.PropTypes.func,
  // from state
  sourceResults: React.PropTypes.array.isRequired,
  collectionResults: React.PropTypes.array.isRequired,
  // from dispatch
  search: React.PropTypes.func.isRequired,
};

const mapStateToProps = state => ({
  sourceResults: state.sources.sourceSearch.list,
  collectionResults: state.sources.collectionSearch.list,
});

const mapDispatchToProps = (dispatch, ownProps) => ({
  search: (searchString) => {
    if ((ownProps.searchCollections === undefined) || (ownProps.searchCollections === true)) {
      dispatch(fetchCollectionSearch(searchString));
    }
    if ((ownProps.searchSources === undefined) || (ownProps.searchSources === true)) {
      dispatch(fetchSourceSearch(searchString));
    }
  },
});

SourceSearchContainer.propTypes = {
  // from context
  intl: React.PropTypes.object.isRequired,
};

export default
  injectIntl(
    connect(mapStateToProps, mapDispatchToProps)(
      SourceSearchContainer
    )
  );
