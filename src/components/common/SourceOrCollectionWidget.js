import PropTypes from 'prop-types';
import React from 'react';
import { Col } from 'react-flexbox-grid/lib';
import { DeleteMediaButton } from './IconButton';

const SourceOrCollectionWidget = (props) => {
  const { object, onDelete, onClick, children } = props;
  const isCollection = object.tags_id !== undefined;

  const typeClass = isCollection ? 'collection' : 'source';
  const objectId = object.id || (isCollection ? object.tags_id : object.media_id);
  const name = isCollection ? (object.name || object.label || object.tag) : (object.name || object.url);
  return (
    <div
      className={`mediaWidget ${typeClass}`}
      key={`mediaWidget${objectId}`}
      onTouchTap={onClick}
    >
      <Col>
        {name}
        {children}
      </Col>
      <Col>
        <DeleteMediaButton onClick={onDelete} />
      </Col>
    </div>
  );
};

SourceOrCollectionWidget.propTypes = {
  object: PropTypes.object.isRequired,
  onDelete: PropTypes.func,
  onClick: PropTypes.func,
  children: PropTypes.node,
};

export default SourceOrCollectionWidget;
