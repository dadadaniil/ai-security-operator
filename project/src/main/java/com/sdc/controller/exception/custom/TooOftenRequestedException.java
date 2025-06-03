package com.sdc.controller.exception.custom;

public class TooOftenRequestedException extends RuntimeException {

    public TooOftenRequestedException() {
    }

    @Override
    public String getMessage() {
        return "The action is requested too often";
    }
}
