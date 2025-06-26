# Home Leave Allowance Report

_Calculated on {{ date }}._

For all plots, the grey dots represent possible flights. On the horizontal axis, the duration of the flight is plotted in minutes. On the vertical axis, the price of the flight is plotted in euros. The red dots represent the best flights possible.
{% for advice in advices %}
## {{ advice.name }}

Flights going from {{ advice.request.departure_airport }} to {{ advice.request.arrival_airport}}. They are travelling with {{ advice.request.family_size }} person(s). They leave on {{ advice.departure_date_str }}{% if advice.return_date_str is not none %} and return on {{advice.return_date_str}}{% endif %}.

![Best flights for {{advice.name}}]({{advice.pareto_path}})

| Duration | Price (€) | Rounded price (€) |{% if advice.request.host_currency.abbreviation != 'EUR'%} Rounded price ({{ advice.request.host_currency.symbol }}) |{% endif %}
| --- | --- | --- |{% if advice.request.host_currency.abbreviation != 'EUR'%} --- |{% endif %}
{% for flight in advice.pareto_flights %}| {{ flight.duration }} | {{ '%.2f' % flight.price }} | {{ flight.rounded_price }} |{% if advice.request.host_currency.abbreviation != 'EUR'%} {{ flight.converted }} |{% endif %}
{% endfor %}
{% endfor %}
