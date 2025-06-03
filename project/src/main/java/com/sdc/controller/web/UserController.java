package com.sdc.controller.web;

import com.sdc.controller.configuration.auth.JwtService;
import com.sdc.controller.exception.custom.InvalidRefreshTokenException;
import com.sdc.model.RefreshToken;
import com.sdc.model.User;
import com.sdc.model.dto.*;
import com.sdc.service.RefreshTokenService;
import com.sdc.service.UserService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Map;

import static org.springframework.http.HttpStatus.*;

@RestController
@RequestMapping("/api/users")
public class UserController {
    @Value("${application.security.jwt.expiration}")
    private long expiration;

    @Value("${application.security.jwt.refresh_expiration}")
    private long refreshExpiration;

    private final UserService userService;
    private final JwtService jwtService;
    private final RefreshTokenService refreshTokenService;

    public UserController(
        UserService userService,
        JwtService jwtService,
        RefreshTokenService refreshTokenService
    ) {
        this.userService = userService;
        this.jwtService = jwtService;
        this.refreshTokenService = refreshTokenService;
    }

    @PostMapping("/signup")
    @ResponseStatus(CREATED)
    public GenericResponse<Map<String, Long>> registerUser(@Valid @RequestBody UserDto user) {
        User createdUser = userService.saveUser(user);
        return GenericResponse.successWithId(CREATED, createdUser.getUserId());
    }

    @PostMapping("/confirm/email")
    @ResponseStatus(OK)
    public GenericResponse<Void> confirmUserAccount(@Valid @RequestBody ConfirmEmailDto confirmEmailDto) {
        userService.confirmEmail(confirmEmailDto.getToken());
        return GenericResponse.success(OK);
    }

    @PostMapping("/resend/confirm/email")
    @ResponseStatus(OK)
    public GenericResponse<Void> resendConfirmEmail(@RequestBody ResendEmailDto resendEmailDTO) {
        userService.resendConfirmEmail(resendEmailDTO.getUserId());
        return GenericResponse.success(OK);

    }

    @PostMapping("/signin")
    @ResponseStatus(OK)
    public GenericResponse<LoginResponse> login(@Valid @RequestBody LoginDto loginDto) {
        boolean isAuthenticated = userService.authenticateUser(loginDto.getEmail(), loginDto.getPassword());
        if (!isAuthenticated) {
            throw new BadCredentialsException("Invalid password");
        }

        final long now = System.currentTimeMillis();
        User user = userService.findUserByEmail(loginDto.getEmail());
        String accessToken = jwtService.generateToken(user, now);

        return GenericResponse.success(
            OK,
            new LoginResponse(
                user.getUserId(),
                createCredentials(
                    accessToken,
                    refreshTokenService.createRefreshToken(user.getUserId()).getToken(),
                    now
                )
            )
        );
    }

    @PostMapping("/reset/password")
    @ResponseStatus(OK)
    public GenericResponse<Void> requestPasswordReset(@Valid @RequestBody RequestResetDto requestResetDto) {
        userService.requestPasswordReset(requestResetDto);
        return GenericResponse.success(OK);
    }

    @PutMapping("/reset/password")
    @ResponseStatus(OK)
    public GenericResponse<Map<String, Long>> resetPassword(@Valid @RequestBody PasswordResetDto passwordResetDto) {
        User user = userService.resetPassword(passwordResetDto);
        return GenericResponse.successWithId(OK, user.getUserId());
    }

    @PostMapping("/refresh")
    @ResponseStatus(OK)
    public GenericResponse<LoginResponse> refreshToken(@RequestBody RefreshTokenDto refreshTokenDto) {
        final String requestRefreshToken = refreshTokenDto.getToken();

        return refreshTokenService.findByToken(requestRefreshToken)
            .map(refreshTokenService::verifyExpiration)
            .map(RefreshToken::getUser)
            .map(user -> {
                final long now = System.currentTimeMillis();
                final String token = jwtService.generateToken(user, now);
                final String refresh = refreshTokenService.createRefreshToken(user.getUserId()).getToken();

                return GenericResponse.success(
                    OK,
                    new LoginResponse(
                        user.getUserId(),
                        createCredentials(token, refresh, now)
                    )
                );
            })
            .orElseThrow(InvalidRefreshTokenException::new);
    }

    @GetMapping
    @ResponseStatus(OK)
    public GenericResponse<User> findUserByEmail(@RequestParam("email") String email) {
        return GenericResponse.success(OK, userService.findUserByEmail(email));
    }

    private Credentials createCredentials(String token, String refresh, long now) {
        return new Credentials(
            token,
            refresh,
            OffsetDateTime.ofInstant(Instant.ofEpochMilli(now + expiration), ZoneOffset.UTC),
            OffsetDateTime.ofInstant(Instant.ofEpochMilli(now + refreshExpiration), ZoneOffset.UTC)
        );
    }

    @GetMapping("/{id}")
    @ResponseStatus(OK)
    @PreAuthorize("hasAnyAuthority('CUSTOMER', 'STUDENT')")
    public GenericResponse<UserLightDto> getUserById(@PathVariable("id") Long id) {
        final User user = userService.findUserById(id);
        return GenericResponse.success(
            OK,
            new UserLightDto(
                user.getFirstName(),
                user.getLastName(),
                user.getRole().getRoleId()
            )
        );
    }
}
