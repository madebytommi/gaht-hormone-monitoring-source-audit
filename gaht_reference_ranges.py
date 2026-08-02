import matplotlib.pyplot as plt
import numpy as np

# Data definitions
protocols = ['Endocrine Society', 'WPATH SOC 8', 'UCSF Guidelines']
categories = [
    'Feminizing Estradiol\n(pg/mL)', 
    'Feminizing Testosterone\n(ng/dL)', 
    'Masculinizing Testosterone\n(ng/dL)'
]

data = {
    'Feminizing Estradiol\n(pg/mL)': [(100, 200), (100, 200), (100, 200)],
    'Feminizing Testosterone\n(ng/dL)': [(0, 50), (0, 50), (0, 55)],
    'Masculinizing Testosterone\n(ng/dL)': [(400, 1000), (350, 1000), (400, 700)]
}

# Create subplots
fig, axes = plt.subplots(1, 3, figsize=(15, 6), sharey=False)
fig.suptitle('GAHT Target Hormone Ranges by Protocol', fontsize=16, fontweight='bold')

colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

for i, category in enumerate(categories):
    ax = axes[i]
    ranges = data[category]
    
    for j, (protocol, (low, high)) in enumerate(zip(protocols, ranges)):
        # Plot the range line
        ax.plot([j, j], [low, high], color=colors[j], marker='o', linewidth=3, markersize=8, label=protocol if i == 0 else "")
        
        # Add text labels for the range values
        y_offset = (high - low) * 0.03 if high != low else 5
        ax.text(j, high + y_offset, f"{high}", ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax.text(j, low - y_offset, f"{low}", ha='center', va='top', fontsize=10, fontweight='bold')

    ax.set_title(category, fontsize=12, pad=15)
    ax.set_xticks(range(len(protocols)))
    ax.set_xticklabels(protocols, rotation=45, ha='right', fontsize=10)
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Adjust y-axis limits to accommodate labels
    min_val = min(r[0] for r in ranges)
    max_val = max(r[1] for r in ranges)
    padding = (max_val - min_val) * 0.15 if max_val != min_val else 10
    ax.set_ylim(min_val - padding, max_val + padding)

fig.legend(loc='upper right', bbox_to_anchor=(0.98, 0.95), title="Protocols")
plt.tight_layout()
plt.subplots_adjust(top=0.82)

# Save the plot
output_file = 'gaht_target_ranges.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Analysis complete. Plot saved successfully to {output_file}")
