package com.sdc.model.dto;

import com.sdc.util.Constants;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;


@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class PasswordResetDto {

    @Size(min = Constants.MINIMAL_PASSWORD_LENGTH, max = Constants.MAXIMUM_PASSWORD_LENGTH,
        message = "password size should be between " + Constants.MINIMAL_PASSWORD_LENGTH +
            " and " + Constants.MAXIMUM_PASSWORD_LENGTH + " characters")
    @NotEmpty(message = "password must not be empty")
    private String password;

    @NotEmpty(message = "token must not be empty")
    private String token;

}
