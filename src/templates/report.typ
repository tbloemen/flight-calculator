= Home Leave Allowance Report

_Generated on #datetime.today().display("[year]-[month]-[day]")._

For all plots, the grey dots represent possible flights. On the horizontal axis, the duration of the flight is plotted in minutes. On the vertical axis, the price of the flight is plotted in euros. The red dots represent the best flights possible.

#let render-advice(advice) = [
  #pagebreak()
  == #advice.name 

  Flights going from #advice.request.departure_airport to #advice.request.arrival_airport. 
  They are travelling with #advice.request.family_size person(s). 
  They leave on #advice.departure_date_str #if advice.return_date_str != none [and return on #advice.return_date_str].

  #figure(
    image(advice.pareto_path, width: 100%),
    caption: [Best flights for #advice.name]
  )
  
  #show table.cell.where(y: 0): strong

  #if advice.request.host_currency.abbreviation != "EUR" {
    table(
      columns: 4,
      table.header[Duration][Price (€)][Rounded price (€)][Rounded price (#advice.request.host_currency.symbol)],
      ..for flight in advice.pareto_flights {
        (flight.duration, str(flight.price), str(flight.rounded_price), str(flight.converted))
      }
    )
  } else {
    table(
      columns: 3,
      table.header[Duration][Price (€)][Rounded price (€)],
      ..for flight in advice.pareto_flights {
        (flight.duration, str(flight.price), str(flight.rounded_price))
      }
    )
  }
]

#let advices = json("advices.json")

#for advice in advices {render-advice(advice)}
