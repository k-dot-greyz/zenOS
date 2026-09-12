# Daily Standup — {{ team }} ({{ date }})

{% for update in updates %}
## {{ update.member }}

- **Yesterday:** {{ update.yesterday }}
- **Today:** {{ update.today }}
- **Blockers:** {{ update.blockers }}

{% endfor %}
{% if notes %}
## Notes

{{ notes }}
{% endif %}
