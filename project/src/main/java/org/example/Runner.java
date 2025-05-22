package org.example;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.*;
import java.util.function.Predicate;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Runner {
    public static void main(String[] args) {
        final String FILENAME = "src/main/resources/in.csv";
        try (Scanner sc = new Scanner(new FileReader(FILENAME))) {
            sc.useDelimiter(";|\\R");  // Use semicolon or newline as delimiter
            Map<Purchase, WeekDay> firstPurchasesMap = new HashMap<>();
            Map<Purchase, WeekDay> lastPurchasesMap = new HashMap<>();
            Map<WeekDay, List<Purchase>> dayPurchasesMap = new EnumMap<>(WeekDay.class);
            List<PricePurchase> pricePurchases = new ArrayList<>();
            while (sc.hasNext()) {
                Purchase currentPurchase = PurchaseFactory.createPurchase(sc);
                if (sc.hasNext()) {
                    WeekDay day = WeekDay.valueOf(sc.next().trim());
                    lastPurchasesMap.put(currentPurchase, day);
                    if (!firstPurchasesMap.containsKey(currentPurchase)) {
                        firstPurchasesMap.put(currentPurchase, day);
                    }
                    List<Purchase> purchases = dayPurchasesMap.getOrDefault(day, new ArrayList<>());
                    purchases.add(currentPurchase);
                    dayPurchasesMap.put(day, purchases);
                    if (currentPurchase instanceof PricePurchase pricePurchase1) {
                        pricePurchases.add(pricePurchase1);
                    }
                }
            }
            sc.close();

            printMap(firstPurchasesMap, "--------mapFirstPurchase--------");
            printMap(lastPurchasesMap, "--------mapLastPurchase--------");
            printMap(dayPurchasesMap, "--------mapEnum--------");
            Purchase targetPurchase = new Purchase("bread", new Euro(155), 0);
            findValueMap(firstPurchasesMap, targetPurchase, "--------First  weekdays for bread with price 1.55--------");
            findValueMap(lastPurchasesMap, targetPurchase, "--------Last  weekdays for bread with price 1.55--------");
            Purchase targetPurchase1 = new Purchase("bread", new Euro(170), 0);
            findValueMap(firstPurchasesMap, targetPurchase1, "--------Another purchase day in firstMap--------");
            EntryChecker<Purchase, WeekDay> meatChecker = new EntryChecker<Purchase, WeekDay>() {
                @Override
                public boolean check(Map.Entry<Purchase, WeekDay> entry) {
                    return entry.getKey().getNAME().equals("meat");
                }
            };
            removeEntries(lastPurchasesMap, meatChecker);

            EntryChecker<Purchase, WeekDay> dayChecker = new EntryChecker<Purchase, WeekDay>() {
                @Override
                public boolean check(Map.Entry<Purchase, WeekDay> entry) {
                    return entry.getValue().equals(WeekDay.FRIDAY);
                }
            };
            removeEntries(firstPurchasesMap, dayChecker);
            printMap(firstPurchasesMap, "removed purchases on Friday");


            System.out.println("--------total cost of first purchase --------");
            totalCost(firstPurchasesMap);
            findValueMap(dayPurchasesMap, WeekDay.MONDAY, "EnumMap");


        } catch (FileNotFoundException e) {
            System.out.println("File was not found");
        }


    }

    private static <Purchase, WeekDay> void printMap(Map<Purchase, WeekDay> map, String message) {
        System.out.println(message);
        for (Map.Entry<Purchase, WeekDay> entry : map.entrySet()) {
            System.out.println(entry.getKey() + "=>" + entry.getValue());
        }
    }

    private static <Purchase, WeekDay> void findValueMap(Map<Purchase, WeekDay> map, Purchase searchKey, String header) {
        if (map.get(searchKey) != null) {
            System.out.println(map.get(searchKey) + " " + header);
        } else System.out.println("Such a day was not found");
    }


    private static <Purchase, WeekDay> void removeEntries(Map<Purchase, WeekDay> map, EntryChecker<Purchase, WeekDay> checker) {
        Iterator<Map.Entry<Purchase, WeekDay>> iterator = map.entrySet().iterator();
        while (iterator.hasNext()) {
            Map.Entry<Purchase, WeekDay> entry = iterator.next();
            if (checker.check(entry)) {
                iterator.remove();
            }
        }
    }

    private static void totalCost(Map<Purchase, WeekDay> map) {
        Euro temp = new Euro();
        for (Map.Entry<Purchase, WeekDay> entry : map.entrySet()) {
            Purchase purchase = entry.getKey();
            temp = temp.add(purchase.getCost());
        }
        System.out.println(temp);
    }
}