package com.sdc.service.annotation;

import com.sdc.model.EntityValidatorType;
import com.sdc.service.annotation.validator.ExistsInDatabaseValidator;
import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Constraint(validatedBy = ExistsInDatabaseValidator.class)
@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
public @interface ExistsInDatabase {
    String message() default "The entity does not exist in the database";

    Class<?>[] groups() default {};

    Class<? extends Payload>[] payload() default {};

    EntityValidatorType entityValidatorType();
}

