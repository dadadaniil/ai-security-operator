package org.example;

import java.util.Objects;

public class Euro {
    private final int VALUE_IN_CENTS;

    public Euro(int value) {
        this.VALUE_IN_CENTS = value;
    }

    public Euro() {
        this.VALUE_IN_CENTS = 0;
    }

    public Euro add(Euro euro) {
        return new Euro(VALUE_IN_CENTS + euro.getVALUE_IN_CENTS());
    }

    public Euro sub(Euro euro) {
        return new Euro(VALUE_IN_CENTS - euro.getVALUE_IN_CENTS());
    }

    public Euro mul(int k) {
        return new Euro(VALUE_IN_CENTS * k);
    }

    public Euro(int euros, int cents) {
        this.VALUE_IN_CENTS = euros * 100 + cents;
    }

    public Euro(Euro euro) {
        this.VALUE_IN_CENTS = euro.getVALUE_IN_CENTS();
    }

    public int getEuro() {
        return VALUE_IN_CENTS / 100;
    }

    public int getCoins() {
        return VALUE_IN_CENTS % 100;
    }

    public int getVALUE_IN_CENTS() {
        return VALUE_IN_CENTS;
    }

    public int compareTo(Euro euro) {
        return Integer.compare(VALUE_IN_CENTS, euro.VALUE_IN_CENTS);
    }

    @Override
    public String toString() {
        return convertToEuro(VALUE_IN_CENTS);
    }

    public String convertToEuro(int value) {
        return String.format("%d.%02d", value / 100, Math.abs(value % 100));
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Euro euro)) return false;
        return VALUE_IN_CENTS == euro.VALUE_IN_CENTS;
    }

    @Override
    public int hashCode() {
        return VALUE_IN_CENTS;
    }
}