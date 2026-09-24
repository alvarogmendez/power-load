# power-load — production plan by merit order

A small **REST API in Flask** that decides how much power each plant must produce to meet a given
electrical load at the lowest cost. It is my solution to the
[GEMS powerplant coding challenge](https://github.com/gems-st-ib/powerplant-coding-challenge) (2024).

## How it works

1. **Cost per MWh** of every plant:
   - gas-fired: gas price / efficiency, plus the CO₂ allowances (0.3 t per MWh);
   - turbojet: kerosine price / efficiency;
   - wind turbines: free, but their maximum output is `pmax × wind %`.
2. **Merit order:** plants are sorted by cost per MWh (quicksort; on a tie the larger plant goes
   first).
3. **Dispatch:** the load is assigned in that order, each plant up to its maximum. If the next
   plant cannot run below its minimum (`pmin`), the previous one is lowered so that the minimum
   fits and the total still matches the load exactly.

## Running it

Requires Python 3.10+ and [Poetry](https://python-poetry.org/).

```bash
git clone https://github.com/alvarogmendez/power-load.git
cd power-load
poetry install
poetry run python app.py          # listens on http://localhost:8888
```

## Example

```bash
curl -X POST http://localhost:8888/productionplan \
  -H "Content-Type: application/json" \
  -d '{
    "load": 480,
    "fuels": {"gas(euro/MWh)": 13.4, "kerosine(euro/MWh)": 50.8, "co2(euro/ton)": 20, "wind(%)": 60},
    "powerplants": [
      {"name": "gasfiredbig1", "type": "gasfired", "efficiency": 0.53, "pmin": 100, "pmax": 460},
      {"name": "gasfiredbig2", "type": "gasfired", "efficiency": 0.53, "pmin": 100, "pmax": 460},
      {"name": "gasfiredsomewhatsmaller", "type": "gasfired", "efficiency": 0.37, "pmin": 40, "pmax": 210},
      {"name": "tj1", "type": "turbojet", "efficiency": 0.3, "pmin": 0, "pmax": 16},
      {"name": "windpark1", "type": "windturbine", "efficiency": 1, "pmin": 0, "pmax": 150},
      {"name": "windpark2", "type": "windturbine", "efficiency": 1, "pmin": 0, "pmax": 36}
    ]
  }'
```

```json
[{"name": "windpark1", "p": 90.0}, {"name": "windpark2", "p": 21.6},
 {"name": "gasfiredbig2", "p": 368.4}, {"name": "gasfiredbig1", "p": 0},
 {"name": "gasfiredsomewhatsmaller", "p": 0}, {"name": "tj1", "p": 0}]
```

The CO₂ cost can be switched off with `co2_active = False` in `app.py`.

## Author

Álvaro González Méndez — [alvarogmendez.es](https://alvarogmendez.es) · [LinkedIn](https://www.linkedin.com/in/alvarogmendez/)
