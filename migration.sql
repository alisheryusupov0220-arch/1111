{\rtf1\ansi\ansicpg1251\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 -- \uc0\u1058 \u1072 \u1073 \u1083 \u1080 \u1094 \u1072  1: \u1055 \u1086 \u1083 \u1100 \u1079 \u1086 \u1074 \u1072 \u1090 \u1077 \u1083 \u1080  \u1080  \u1056 \u1086 \u1083 \u1080 \
CREATE TABLE IF NOT EXISTS Users (\
    id INTEGER PRIMARY KEY AUTOINCREMENT,\
    telegram_id INTEGER UNIQUE,\
    username TEXT,\
    full_name TEXT NOT NULL,\
    -- \uc0\u1056 \u1086 \u1083 \u1080 : 'owner', 'manager', 'cashier'\
    role TEXT NOT NULL DEFAULT 'cashier', \
    is_active INTEGER DEFAULT 1,\
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\
);\
\
-- \uc0\u1058 \u1072 \u1073 \u1083 \u1080 \u1094 \u1072  2: \u1054 \u1073 \u1097 \u1080 \u1081  \u1058 \u1072 \u1081 \u1084 \u1083 \u1072 \u1081 \u1085  \u1057 \u1086 \u1073 \u1099 \u1090 \u1080 \u1081  (\u1046 \u1091 \u1088 \u1085 \u1072 \u1083  \u1040 \u1091 \u1076 \u1080 \u1090 \u1072 )\
CREATE TABLE IF NOT EXISTS Audit_Timeline (\
    id INTEGER PRIMARY KEY AUTOINCREMENT,\
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
    user_id INTEGER NOT NULL,\
    operation_type TEXT NOT NULL, -- 'expense', 'income', 'transfer'\
    amount REAL NOT NULL,\
    category_id INTEGER,\
    category_type TEXT,\
    account_id INTEGER,\
    description TEXT,\
    source TEXT,\
    FOREIGN KEY (user_id) REFERENCES Users(id)\
);}