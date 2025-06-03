package com.sdc.controller.exception.custom;

public class InvalidUserIdException extends RuntimeException {
    public InvalidUserIdException() {
    }

    @Override
    public String getMessage() {
        return "Invalid user id";
    }
}
