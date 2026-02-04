import React from 'react';

interface FeaturesListProps {
  attributes: Record<string, any> | null;
}

const FeaturesList: React.FC<FeaturesListProps> = ({ attributes }) => {
  if (!attributes || Object.keys(attributes).length === 0) {
    return null;
  }

  return (
    <div className="mt-6">
      <h3 className="text-xl font-semibold mb-3">Features</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {Object.entries(attributes).map(([key, value]) => (
          <div key={key} className="p-3 bg-gray-50 rounded shadow-sm border border-gray-100">
            <span className="font-medium capitalize text-gray-700">{key.replace(/_/g, ' ')}:</span>
            <span className="ml-2 text-gray-900">{String(value)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FeaturesList;
