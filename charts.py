
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt

def plot_step_times(steps: list[dict]):
    """Стовпчики: скільки секунд пішло на кожен крок."""
    if not steps:
        return None
        
    names = []   
    times = []   

    
    for s in steps:
        names.append(str(s["node_id"]))
        times.append(s["time"])

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(names, times) # Малюємо стовпчики (колір буде стандартний)
    ax.set_xlabel("Крок")
    ax.set_ylabel("Секунди")
    ax.set_title("Час на кожен крок")
    
    return fig


def plot_results_pie(steps: list[dict]):
    """Кругова діаграма: ok / mistake / fatal."""
    if not steps:
        return None
        
    
    ok_count = 0
    mistake_count = 0
    fatal_count = 0

    
    for s in steps:
        if s["result"] == "ok":
            ok_count += 1
        elif s["result"] == "mistake":
            mistake_count += 1
        elif s["result"] == "fatal":
            fatal_count += 1

    sizes = []
    labels = []

    
    if ok_count > 0:
        sizes.append(ok_count)
        labels.append("Правильно")
        
    if mistake_count > 0:
        sizes.append(mistake_count)
        labels.append("Помилка")
        
    if fatal_count > 0:
        sizes.append(fatal_count)
        labels.append("Критична")

    
    if not sizes:
        return None

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(sizes, labels=labels, autopct="%1.0f%%") # Колір теж буде стандартний
    ax.set_title("Результати проходження")
    
    return fig
