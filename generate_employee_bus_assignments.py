import pandas as pd

# Load clustered employee locations
employees_df = pd.read_csv("locations_all_with_pick_up_location.csv")
# Load pickup point to bus assignment
bus_points_df = pd.read_csv("bus_points_with_bus_numbers.csv")

# Merge on pickup cluster ID
merged = pd.merge(employees_df, bus_points_df, left_on='cluster', right_on='pickup_point', how='left')


# Define bus size by employee count at pickup
def bus_size(count):
    if count <= 18:
        return "Small (18)"
    elif count <= 27:
        return "Medium (27)"
    else:
        return "Large (45)"


merged["bus_size"] = merged["employee_count"].apply(bus_size)

# Save final assignment file
merged[["id", "cluster", "bus_number", "bus_size"]].to_csv("employee_bus_assignments.csv", index=False)
print("✅ Saved: employee_bus_assignments.csv")
