package org.example;

import java.text.DecimalFormat;
import java.util.Objects;

public class Purchase {
    public int COUNT;
    public String NAME;
    public Euro PRICE;


    public Purchase(String NAME, Euro PRICE, int COUNT) {
        this.COUNT = COUNT;
        this.NAME = NAME;
        this.PRICE = PRICE;
    }


    public void setCOUNT(int COUNT) {
        this.COUNT = COUNT;
    }

    public void setNAME(String NAME) {
        this.NAME = NAME;
    }

    public void setPRICE(Euro PRICE) {
        this.PRICE = PRICE;
    }

    public Purchase() {
    }

    public int getCOUNT() {
        return COUNT;
    }

    public String getNAME() {
        return NAME;
    }

    public Euro getPRICE() {
        return PRICE;
    }

    public Euro getCost() {

        return PRICE.mul(COUNT);
    }

    public String toString() {
        DecimalFormat df = new DecimalFormat("#.00");
        String var10000 = this.getClass().getSimpleName();
        return var10000 + "; " + this.NAME + "; " + this.COUNT + "; " + this.PRICE.toString();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Purchase purchase)) return false;
        return this.NAME.equals(purchase.NAME) && this.PRICE.equals(purchase.PRICE);
    }

    @Override
    public int hashCode() {
        int result = this.NAME.hashCode();
        result = 31 * result + this.PRICE.hashCode();
        return result;
    }
}
