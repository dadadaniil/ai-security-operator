package com.sdc.controller.exception.custom;

public class InvalidTokenException extends RuntimeException {
    public InvalidTokenException() {
    }

    @Override
    public String getMessage() {
        return "Confirmation token is invalid";
    }
}
