package com.sdc.controller.exception.custom;

public class EmailAlreadyVerifiedException extends RuntimeException {
    private final Long userId;

    private EmailAlreadyVerifiedException(Long userId) {
        this.userId = userId;
    }

    public static EmailAlreadyVerifiedException createWith(Long userId) {
        return new EmailAlreadyVerifiedException(userId);
    }

    @Override
    public String getMessage() {
        return "Email is already verified for user with id '" + userId + "'";
    }
}

