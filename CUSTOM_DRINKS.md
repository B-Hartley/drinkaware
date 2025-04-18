# Drinkaware Integration: Custom Drinks Guide

The Drinkaware integration supports both predefined drink types and custom drinks that may be created in the Drinkaware app.

## Understanding Custom Drinks

Custom drinks are created within the Drinkaware app and are assigned unique IDs that work just like the predefined drink types. From the perspective of Home Assistant, there's no functional difference between a predefined drink type and a custom drink - both are identified by UUIDs.

## How Custom Drinks are Handled

1. **Predefined Drink Types**: These are available in the dropdown menus in Home Assistant's service UI.

2. **Your Custom Drinks**: We've included several known custom drinks in the dropdown:
   - Corona 330ml (4.5% ABV)
   - Wingman A.F. (0.5% ABV)
   - Tequila - Custom (45.0% ABV)

3. **Adding Your Own Custom Drinks**: If you have custom drinks not listed in the dropdown:
   
   a. To find the ID of your custom drink:
      - You'll need to use a network capture tool like MITM Proxy to inspect the traffic from the Drinkaware app
      - Look for the `drinkId` parameter when a drink is added
      
   b. To use your custom drink in Home Assistant:
      - Select "Custom Drink (enter ID manually)" from the dropdown
      - Replace the value "custom" with your actual drink ID before submitting the service call

## Example: Using a Custom Drink

If you've identified a custom drink with ID `1A2B3C4D-5E6F-7890-ABCD-EF1234567890`:

```yaml
service: drinkaware.log_drink
data:
  account_name: "John's Drinkaware"
  drink_id: "1A2B3C4D-5E6F-7890-ABCD-EF1234567890"  # Your custom drink ID
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint
  abv: 5.2  # Custom ABV if needed
  quantity: 1
```

## Additional Tips

1. **ABV Values**: For custom drinks, you can specify a custom ABV value. If not provided, the default ABV associated with the drink type will be used.

2. **Custom Measures**: Similar to custom drinks, the Drinkaware app may use custom measure sizes. If you need to use a custom measure:
   - Select "Custom Measure (enter ID manually)" from the dropdown
   - Replace the value "custom" with your actual measure ID

3. **Adding to the Dropdown**: If you'd like to add your frequently used custom drinks to the dropdown permanently, you can modify the `services.yaml` file in the integration directory to include your own custom options.