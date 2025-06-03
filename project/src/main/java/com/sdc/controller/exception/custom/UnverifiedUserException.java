package com.sdc.controller.exception.custom;

public class UnverifiedUserException extends RuntimeException {
    private final Long userId;

    private UnverifiedUserException(Long userId) {
        this.userId = userId;
    }

    public static UnverifiedUserException createWith(Long userId) {
        return new UnverifiedUserException(userId);
    }

    @Override
    public String getMessage() {
        return "User '" + userId + "' is not verified";
    }
}
