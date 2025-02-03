CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    conceptType VARCHAR(100) NOT NULL,
    conceptUri VARCHAR(255) UNIQUE NOT NULL,
    skillType VARCHAR(100),
    reuseLevel VARCHAR(50),
    preferredLabel VARCHAR(255) NOT NULL,
    altLabels TEXT,
    hiddenLabels TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    modifiedDate TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    scopeNote TEXT,
    definition TEXT,
    inScheme TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX idx_concepts_preferredlabel ON skills(preferredLabel);
