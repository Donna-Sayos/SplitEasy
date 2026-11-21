PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS ParticipantItems;
DROP TABLE IF EXISTS BillParticipants;
DROP TABLE IF EXISTS Bills;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS StateTaxes;
CREATE TABLE StateTaxes (
    state_code TEXT PRIMARY KEY,
    state_name TEXT NOT NULL,
    tax_rate FLOAT NOT NULL
);
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    state_code TEXT NOT NULL,
    FOREIGN KEY (state_code) REFERENCES StateTaxes(state_code)
);
CREATE TABLE Bills (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bill_title TEXT NOT NULL,
    split_mode TEXT NOT NULL,
    subtotal FLOAT NOT NULL,
    tip_percent FLOAT NOT NULL,
    tax_amount FLOAT NOT NULL,
    tip_amount FLOAT NOT NULL,
    total_amount FLOAT NOT NULL,
    entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
CREATE TABLE BillParticipants (
    participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    participant_name TEXT NOT NULL,
    owed_amount FLOAT NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES Bills(bill_id) ON DELETE CASCADE
);
CREATE TABLE ParticipantItems (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    item_price FLOAT NOT NULL,
    FOREIGN KEY (participant_id) REFERENCES BillParticipants(participant_id) ON DELETE CASCADE
);
INSERT INTO StateTaxes (state_code, state_name, tax_rate)
VALUES ('AL', 'Alabama', 0.0400),
    ('AK', 'Alaska', 0.0000),
    ('AZ', 'Arizona', 0.0560),
    ('AR', 'Arkansas', 0.0650),
    ('CA', 'California', 0.0725),
    ('CO', 'Colorado', 0.0290),
    ('CT', 'Connecticut', 0.0635),
    ('DE', 'Delaware', 0.0000),
    ('DC', 'District of Columbia', 0.0600),
    ('FL', 'Florida', 0.0600),
    ('GA', 'Georgia', 0.0400),
    ('HI', 'Hawaii', 0.0400),
    ('ID', 'Idaho', 0.0600),
    ('IL', 'Illinois', 0.0625),
    ('IN', 'Indiana', 0.0700),
    ('IA', 'Iowa', 0.0600),
    ('KS', 'Kansas', 0.0650),
    ('KY', 'Kentucky', 0.0600),
    ('LA', 'Louisiana', 0.0445),
    ('ME', 'Maine', 0.0550),
    ('MD', 'Maryland', 0.0600),
    ('MA', 'Massachusetts', 0.0625),
    ('MI', 'Michigan', 0.0600),
    ('MN', 'Minnesota', 0.0688),
    ('MS', 'Mississippi', 0.0700),
    ('MO', 'Missouri', 0.0423),
    ('MT', 'Montana', 0.0000),
    ('NE', 'Nebraska', 0.0550),
    ('NV', 'Nevada', 0.0685),
    ('NH', 'New Hampshire', 0.0000),
    ('NJ', 'New Jersey', 0.0663),
    ('NM', 'New Mexico', 0.0488),
    ('NY', 'New York', 0.0400),
    ('NC', 'North Carolina', 0.0475),
    ('ND', 'North Dakota', 0.0500),
    ('OH', 'Ohio', 0.0575),
    ('OK', 'Oklahoma', 0.0450),
    ('OR', 'Oregon', 0.0000),
    ('PA', 'Pennsylvania', 0.0600),
    ('RI', 'Rhode Island', 0.0700),
    ('SC', 'South Carolina', 0.0600),
    ('SD', 'South Dakota', 0.0420),
    ('TN', 'Tennessee', 0.0700),
    ('TX', 'Texas', 0.0625),
    ('UT', 'Utah', 0.0485),
    ('VT', 'Vermont', 0.0600),
    ('VA', 'Virginia', 0.0530),
    ('WA', 'Washington', 0.0650),
    ('WV', 'West Virginia', 0.0600),
    ('WI', 'Wisconsin', 0.0500),
    ('WY', 'Wyoming', 0.0400);