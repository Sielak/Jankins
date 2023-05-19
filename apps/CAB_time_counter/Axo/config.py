RESOURCES = {
    "me": {
        "address": "me",
        "verbs": ["GET"],
        "required": []
    },
    "features": {
        "address": "features",
        "verbs": ["GET", "POST", "DELETE"],
        "required": ["item"],
        "resources": ["attachments", "comments", "emails", "notifications"]
    },
    "defects": {
        "address": "defects",
        "verbs": ["GET", "POST", "DELETE"],
        "required": ["item"],
        "resources": ["attachments", "comments", "emails", "notifications"]
    },
    "incidents": {
        "address": "incidents",
        "verbs": ["GET", "POST", "DELETE"],
        "required": ["item"],
        "resources": ["attachments", "comments", "emails", "notifications"]
    },
    "releases": {
        "address": "releases",
        "verbs": ["GET", "POST", "DELETE"],
        "required": ["name", "release_type"]
    },
    "fields": {
        "address": "fields",
        "verbs": ["GET"],
        "required": []
    },
    "filters": {
        "address": "filters",
        "verbs": ["GET"],
        "required": []
    },
    "activity": {
        "address": "activity",
        "verbs": ["GET"],
        "required": []
    },
    "customers": {
        "address": "customers",
        "verbs": ["GET", "POST", "DELETE"],
        "required": ["company_name"]
    },
    "users": {
        "address": "users",
        "verbs": ["GET", "POST", "DELETE"],
        "required": ["first_name", "last_name", "security_roles"]
    },
    "projects": {
        "address": "projects",
        "verbs": ["GET", "POST", "DELETE"],
        "required": ["name"],
        "resources": ["attachments", "workflow"]
    },
    "work_logs": {
        "address": "work_logs",
        "verbs": ["GET"],
        "required": []
    },
    "teams": {
        "address": "teams",
        "verbs": ["GET"],
        "required": []
    },
    "picklists": {
        "address": "picklists",
        "verbs": ["GET"],
        "required": ["picklist_type"],
        "resources": ["priority", "status", "severity", "category", "time_units", "work_log_types", "item_relations",
                      "release_types", "release_status", "escalation", "custom"]
    },
    "workflow_steps": {
        "address": "workflow_steps",
        "verbs": ["GET"],
        "required": []
    },
    "workflows": {
        "address": "workflows",
        "verbs": ["GET"],
        "required": []
    },
    "tasks": {
        "address": "tasks",
        "verbs": ["GET", "POST", "DELETE"],
        "required": ["item"],
        "resources": ["attachments", "comments", "emails", "notifications"]
    },
}
