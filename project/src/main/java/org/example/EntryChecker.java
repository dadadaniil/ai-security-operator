package org.example;


import java.util.Map;

public interface EntryChecker<Purchase, WeekDay> {
    boolean check(Map.Entry<Purchase, WeekDay> entry);
}