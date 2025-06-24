# Home Leave Allowance Report

_Calculated on {{ date }}._

For all plots, the grey dots represent possible flights. On the horizontal axis, the duration of the flight is plotted in minutes. On the vertical axis, the price of the flight is plotted in euros. The red dots represent the best flights possible.
{% for advice in advices %}
## {{ advice.name }}

![Best flights for {{advice.name}}]({{advice.pareto_path}})
{% for flight in advice.pareto_flights %}
- This flight costs **€ {{ '%.2f' % flight.price }}**. It takes {{ flight.duration }}. Rounded, the allowance would be **€ {{ flight.rounded_price }}**.{% if advice.currency.abbreviation != 'EUR'%} That is **{{ flight.converted }}**.{% endif %}{% endfor %}
{% endfor %}
