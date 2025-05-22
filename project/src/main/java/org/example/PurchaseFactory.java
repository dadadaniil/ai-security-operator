package org.example;

import java.util.Scanner;

public class PurchaseFactory {
    public static Purchase createPurchase(Scanner scanner) {
        String name = scanner.next();
        int price = Integer.parseInt(scanner.next());
        int quantity = Integer.parseInt(scanner.next());
        
        if (scanner.hasNextInt()) {
            int discount = Integer.parseInt(scanner.next());
            return new PricePurchase(name, new Euro(price), quantity, new Euro(discount));
        } else {
            return new Purchase(name, new Euro(price), quantity);
        }
    }
}

