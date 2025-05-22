package org.example;

import java.util.concurrent.ExecutionException;

public class PricePurchase extends Purchase {
    private Euro discount;

    public PricePurchase() {
        super();
        this.discount = null;
    }

    public PricePurchase(String NAME, Euro price, int COUNT, Euro discount) {
        super(NAME,price,COUNT);
        this.discount = discount;
    }



    public Euro getDiscount() {
        return discount;
    }

    public void setDiscount(Euro discount) {
        this.discount = discount;
    }

    @Override
    public Euro getCost() {
        Euro bufCost = this.PRICE.sub(discount);
            return new Euro( bufCost.getVALUE_IN_CENTS()*COUNT);
        }
    @Override
    public String toString() {

        return super.toString()+ "; " +this.discount.toString();
    }

}
