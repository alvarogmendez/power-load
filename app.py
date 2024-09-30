from flask import Flask, request
import json

app = Flask(__name__)

co2_active = True

@app.post('/productionplan')
def production_plan_post():
    request_data = request.get_json()
    plants_consumption = []
    for plant in request_data["powerplants"]:
        plants_consumption.append(calc_plant_consumption(plant,request_data["fuels"]))
    quickshort_plants(plants_consumption,0,len(plants_consumption)-1)
    load = request_data["load"]
    answr = []
    for plant in plants_consumption:
        power = 0
        if plant["pmin"] < load:
            if plant["pow"] <= load:
                power = plant["pow"]
                load -= power
            else:
                power = load
                load = 0
        answr.append({
            "name": plant["name"],
            "p": round(power,1) 
        })
    
    return json.dumps(answr)
    
def quickshort_plants(plants: list, low: int, high: int):
    if low < high:
        piv_pointer = part_short(plants, low, high)
        quickshort_plants(plants, low, piv_pointer - 1)
        quickshort_plants(plants, piv_pointer + 1, high)
    
def part_short(plants: list, low: int, high: int) -> int:
    i = low -1
    for j in range(low, high):
        
        if plants[j]["unit_cost"] == plants[high]["unit_cost"] == 0:
            if plants[j]["pow"] > plants[high]["pow"]:
                i += 1
                (plants[i], plants[j]) = (plants[j], plants[i])
        elif plants[j]["unit_cost"] <= plants[high]["unit_cost"]:
            i += 1
            (plants[i], plants[j]) = (plants[j], plants[i])
    (plants[high],plants[i+1]) = (plants[i+1],plants[high])
    return i + 1
    

def calc_plant_consumption(plant: dict, fuels: dict, pow: int = -1) -> dict:
    if pow == -1: pow = plant["pmax"]
    res_values = {
        "cost": 0,
        "pow": pow,
        "name": plant["name"],
        "unit_cost" : 0,
        "pmin": plant["pmin"],
    }
    match plant["type"]:
        case "gasfired":
            if co2_active: co2_tons_allowance = pow * .3 * fuels["co2(euro/ton)"]
            else: co2_tons_allowance = 0
            gas_cost = pow * fuels["gas(euro/MWh)"] / plant["efficiency"]
            res_values["cost"] = co2_tons_allowance + gas_cost
            res_values["unit_cost"] = res_values["cost"] / res_values["pow"]
        case "turbojet":
            res_values["cost"] = pow * fuels["kerosine(euro/MWh)"] / plant["efficiency"]
            res_values["unit_cost"] = res_values["cost"] / res_values["pow"]
        case "windturbine":
            res_values["pow"] = plant["pmax"] * fuels["wind(%)"] / 100
    return res_values

if __name__ == '__main__':
    app.run(port=8888)