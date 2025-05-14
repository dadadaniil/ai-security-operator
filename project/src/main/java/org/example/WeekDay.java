package org.example;

public enum WeekDay {
    MONDAY(1),
    TUESDAY(2),
    WEDNESDAY(3),
    THURSDAY(4),
    FRIDAY(5),
    SATURDAY(6),
    SUNDAY(7);
    private final int value;
    WeekDay(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

}