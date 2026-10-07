def shipping_cost(total, express):
    cost = 5
    if total >= 50:
        cost = 0
    if express:
        cost += 10
    return cost


shipping_cost(60, True)
