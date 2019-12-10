import PropTypes from 'prop-types';
import React from 'react';
import { FormattedMessage, injectIntl } from 'react-intl';
import { EditButton, AddButton } from './IconButton';

const localMessages = {
  platform: { id: 'platform.manage.platform',
    defaultMessage: 'Platform' },
  seedQueryDescription: { id: 'platform.manage.seedQuery', defaultMessage: 'Seed Query' },
  addOrEditOrRemove: { id: 'platform.manage.whatToDo',
    defaultMessage: 'Add or Edit or Remove (TBD)' },
};

const PlatformTable = props => {
  const latestWeb = props.platforms.filter(s => s.platform === 'web').reduce((a, b) => (a.topic_seed_queries_id > b.topic_seed_queries_id ? a : b));
  const latestTwitter = props.platforms.filter(s => s.platform === 'twitter').reduce((a, b) => (a.topic_seed_queries_id > b.topic_seed_queries_id ? a : b));
  const latestReddit = props.platforms.filter(s => s.platform === 'reddit').reduce((a, b) => (a.topic_seed_queries_id > b.topic_seed_queries_id ? a : b));
  const latestPlatforms = [latestWeb, latestTwitter, latestReddit];
  return (
    <div className="platform-table">
      <table width="100%">
        <tbody>
          <tr>
            <th><FormattedMessage {...localMessages.platform} /></th>
            <th><FormattedMessage {...localMessages.seedQueryDescription} /></th>
            <th><FormattedMessage {...localMessages.addOrEditOrRemove} /></th>
          </tr>
          {latestPlatforms.map((c, idx) => (
            <tr key={c.type} className={(idx % 2 === 0) ? 'even' : 'odd'}>
              <td>
                {c.platform}
              </td>
              <td>
                {c.query}
              </td>
              <td>
                {c.topic_seed_queries_id > -1 ? <EditButton onClick={() => props.onEditClicked(c.topic_seed_queries_id, c.type)} /> : <AddButton onClick={() => props.onAddClicked(c.type)} />}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

PlatformTable.propTypes = {
  // from parent
  platforms: PropTypes.array.isRequired,
  onEditClicked: PropTypes.func.isRequired,
  onAddClicked: PropTypes.func.isRequired,
  // from context
  intl: PropTypes.object.isRequired,
};

export default
injectIntl(
  PlatformTable
);
