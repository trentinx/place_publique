import matplotlib.pyplot as plt


def plot_accuracies(all_confidences, class_stats, total_frames):
    if not all_confidences:
        return

    accuracy = sum(c > 0.7 for c in all_confidences) / len(all_confidences) * 100

    class_names = list(class_stats.keys())
    map_scores = [
        (class_stats[c]['total_conf'] / class_stats[c]['count']) * 100
        for c in class_names
    ]

    plt.figure(figsize=(10, 5))
    plt.bar(class_names, map_scores)
    plt.ylabel("MAP (%)")
    plt.title("MAP par classe")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
