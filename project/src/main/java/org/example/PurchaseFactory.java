package org.example;

import java.util.Scanner;

public class PurchaseFactory {
    public static Purchase createPurchase(Scanner scanner) {
        String line = scanner.nextLine();
        String[] data = line.split(";");
        switch (data.length) {
            case 3 -> {

                return new Purchase(data[0], new Euro(Integer.parseInt(data[2])),Integer.parseInt(data[3]));
            }
            case 4 -> {

                return new PricePurchase((data[0]), new Euro(Integer.parseInt(data[2])),Integer.parseInt(data[3]),new Euro(Integer.parseInt(data[4])));
            }
            default -> throw new IllegalStateException("Unexpected value: " + data.length);
        }
    }
}

