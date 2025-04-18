# Available Drinks and Measures in Drinkaware

This document lists the available drink types and measures extracted from the Drinkaware API.

## Drink Categories

### Beer
- Lager (`FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7`): 4.0% ABV
- Beer (`D4F06BD4-1F61-468B-AE86-C6CC2D56E021`): 5.0% ABV
- Ale/stout (`1F8DF28A-5F05-470E-833B-06C499965C99`): 4.5% ABV

### Wine
- White Wine (`E3DEDBFD-63CE-492D-8E3E-9C24010227D8`): 13.0% ABV
- Red Wine (`19E82B28-9AD5-4546-A966-13B27EC6E4FB`): 13.0% ABV
- Rosé Wine (`FA3B43D0-A418-4F4D-8FC1-218E8DA81918`): 13.0% ABV
- Champagne (`61C3F476-24D1-46DB-9FA0-613ED4082531`): 12.0% ABV
- Prosecco (`5184149E-450E-4A63-92E5-19AD7F49FCD1`): 12.0% ABV

### Spirits
- Vodka (`0E3CA732-21D6-4631-A60C-155C2BB85C18`): 40.0% ABV
- Gin (`FECCEBB8-68D1-4BF1-B42F-7BB6C919B0F0`): 40.0% ABV
- Tequila (`32B22A73-D900-43E1-AAB6-8ADC27590B5D`): 50.0% ABV
- Rum (`780B45E2-26D6-4F55-A0C1-75868835D672`): 40.0% ABV
- Whisk(e)y (`2AAE4A2E-8C0A-40E1-BCDE-EB986111D2DE`): 40.0% ABV
- Brandy (`E473445D-2B75-47DA-9978-24C80093B1D0`): 40.0% ABV
- Other Spirit (`300546E3-DB89-49DC-B4B5-8ED96EB18C12`): 40.0% ABV

### Fortified Wines
- Port/Sherry (`F8486573-6F92-4B63-BAEB-3E76B750E14D`): 18.0% ABV

### Cider
- Cider (`61AD633A-7366-4497-BD36-9078466F00FE`): 4.5% ABV

### Alcopops
- Alcopop (`0B2A65CA-5EC4-46B6-9E4D-6E0DDC8D57B8`): 4.0% ABV

### Custom Drinks (from MITM log)
- corona 330ml (`E44AE744-1318-4978-8C84-E143C2B0AE3B`): 4.5% ABV (derived from Lager)
- Wingman A.F. (`B515F736-F194-4ED4-A7A9-EA2D75CC51AD`): 0.5% ABV (derived from Lager)
- Tequila (`4DDB9B89-CCB5-471E-A03C-AC516AE4E821`): 45.0% ABV (custom version of standard Tequila)

## Available Measures

### Beer and Cider Measures
- Pint (`B59DCD68-96FF-4B4C-BA69-3707D085C407`): 0.568 liters
- Half pint (`174F45D7-745A-45F0-9D44-88DA1075CE79`): 0.284 liters
- Small bottle/can (`6B56A1FB-33A1-4E51-BED7-536751DE56BC`): 0.33 liters
- Bottle/can (`0CB11B53-6E3C-4C47-A2E9-68BA40DFFE13`): 0.44 liters
- Bottle (`8F185B18-2A82-4D1A-A1F7-20E01D5E2FEC`): 0.5 liters
- Large bottle (`03D87F35-A1DF-40EE-9398-FA1CA55DD894`): 0.66 liters

### Wine Measures
- Small glass (`0E40AE5F-098D-4826-ADCA-298A6A14F514`): 0.125 liters
- Medium glass (`E586C800-24CA-4942-837A-4CD2CBF8338A`): 0.175 liters
- Large glass (`6450132A-F73F-414A-83BB-43C37B40272F`): 0.25 liters

### Champagne and Prosecco Measures
- Glass (`B6CFC69E-0E85-4F82-A109-155801BB7C79`): 0.125 liters
- Medium glass (`A8B1FA3D-25A2-4685-92E9-DE9D19407CE3`): 0.187 liters

### Spirit Measures
- Single measure (`A83406D4-741F-49B4-B310-8B7DEB8B072F`): 0.025 liters
- Double measure (`FCCC81A2-3BFF-45C0-832F-BCF73E81D0D1`): 0.05 liters

### Port/Sherry Measures
- Small glass (`021703DD-248C-4A51-ACFD-0CE97540C8EC`): 0.075 liters

## Using These IDs in Home Assistant

When using the `drinkaware.log_drink` service, you'll need to specify both the `drink_id` and the `measure_id` parameters. For example, to log a pint of lager:

```yaml
service: drinkaware.log_drink
data:
  entry_id: your_config_entry_id
  drink_id: "FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7"  # Lager
  measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"  # Pint
  quantity: 1
```

The assistant can also create scripts for common drink types to make logging easier. For example:

```yaml
script:
  log_pint_of_lager:
    alias: "Log a pint of lager"
    sequence:
      - service: drinkaware.log_drink
        data:
          entry_id: your_config_entry_id
          drink_id: "FAB60DBF-911F-4286-9C3E-0F0BCB40E3B7"
          measure_id: "B59DCD68-96FF-4B4C-BA69-3707D085C407"
          quantity: 1
```