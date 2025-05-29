package com.sdc.service;

import com.sdc.controller.exception.custom.*;
import com.sdc.model.ConfirmationToken;
import com.sdc.model.Role;
import com.sdc.model.User;
import com.sdc.model.dto.PasswordResetDto;
import com.sdc.model.dto.RequestResetDto;
import com.sdc.model.dto.UserDto;
import com.sdc.repository.ConfirmationTokenRepository;
import com.sdc.repository.RoleRepository;
import com.sdc.repository.UserRepository;
import com.sdc.util.Constants;
import com.sdc.util.PasswordUtil;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Spy;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.beans.factory.annotation.Autowired;

import java.time.OffsetDateTime;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class UserServiceImplTest {
    private static final long VERIFIED_USER_ID = 1L;
    private static final long UNVERIFIED_USER_ID = 2L;
    private static final long ROLE_ID = 2L;

    @Mock
    private Constants constants;

    @Mock
    private ConfirmationTokenService confirmationTokenService;
    @Mock
    private UserRepository userRepository;
    @Mock
    private RoleRepository roleRepository;
    @Mock
    private ConfirmationTokenRepository confirmationTokenRepository;
    @Mock
    private EmailService emailService;
    @Mock
    private PasswordUtil passwordUtil;
    @Spy
    @InjectMocks
    private UserServiceImpl userService;

    private Role role;
    private User user;
    private User unverifiedUser;
    private UserDto userDto;

    @BeforeEach
    public void beforeEach() {
        role = new Role();
        role.setRoleId(ROLE_ID);
        role.setName("name");
        role.setDescription("description");
        constants.tokenValidHours = 1;


        user = new User(
            VERIFIED_USER_ID,
            "UserName",
            "UserLastName",
            "email",
            "password",
            null,
            true,
            0L,
            0L,
            OffsetDateTime.now(),
            OffsetDateTime.now(),
            null,
            null
        );
        unverifiedUser = new User(
            UNVERIFIED_USER_ID,
            "",
            "",
            "",
            "old password",
            null,
            false,
            0L,
            0L,
            OffsetDateTime.now(),
            OffsetDateTime.now(),
            null, null
        );

        userDto = new UserDto("UserName", "UserLastName", "password", "email", ROLE_ID);
    }

    @DisplayName("Test for saveUser()")
    @Test
    public void testSaveNewUserReturnsUserObject() {
        when(userRepository.existsByEmail(anyString())).thenReturn(false);
        when(roleRepository.getReferenceById(anyLong())).thenReturn(role);
        when(userRepository.save(any(User.class))).thenReturn(user);
        when(confirmationTokenRepository.save(any(ConfirmationToken.class))).thenReturn(new ConfirmationToken(user));
        doNothing().when(emailService).sendConfirmationEmail(anyString(), anyString());

        User savedUser = userService.saveUser(userDto);

        assertNotNull(savedUser);
    }

    @DisplayName("Test for saveUser() with used email")
    @Test
    public void testSaveNewUserThrowsEmailInUseException() {
        when(userRepository.existsByEmail(anyString())).thenReturn(true);

        assertThrows(EmailInUseException.class, () -> userService.saveUser(userDto));

        verify(userRepository, never()).save(any(User.class));
    }

    @DisplayName("Test for confirmEmail()")
    @Test
    public void testConfirmEmailVerifiesUser() {
        ConfirmationToken token = new ConfirmationToken(unverifiedUser);

        when(confirmationTokenRepository.findByConfirmationToken(token.getConfirmationToken()))
            .thenReturn(Optional.of(token));
        when(userRepository.findById(token.getUser().getUserId()))
            .thenReturn(Optional.ofNullable(unverifiedUser));
        when(userRepository.save(unverifiedUser)).thenReturn(unverifiedUser);

        userService.confirmEmail(token.getConfirmationToken());

        assertTrue(unverifiedUser.isVerified());
    }

    @DisplayName("Test for confirmEmail() with invalid token")
    @Test
    public void testConfirmEmailThrowsInvalidTokenException() {
        String invalidToken = "invalid_token";
        when(confirmationTokenRepository.findByConfirmationToken(invalidToken)).thenReturn(Optional.empty());

        assertThrows(InvalidTokenException.class, () -> userService.confirmEmail(invalidToken));

        verify(userRepository, never()).save(any(User.class));
    }

    @DisplayName("Test for confirmEmail() with invalid user")
    @Test
    public void testConfirmEmailThrowsNoSuchUserIdException() {
        ConfirmationToken confirmationToken = new ConfirmationToken(user);
        when(confirmationTokenRepository.findByConfirmationToken(confirmationToken.getConfirmationToken()))
            .thenReturn(Optional.of(confirmationToken));
        when(userRepository.findById(user.getUserId()))
            .thenReturn(Optional.empty());

        assertThrows(
            NoSuchUserIdException.class,
            () -> userService.confirmEmail(confirmationToken.getConfirmationToken())
        );

        verifyNoMoreInteractions(confirmationTokenRepository, userRepository);
    }

    @DisplayName("Test for authenticateUser()")
    @Test
    public void testAuthenticateUserReturnsTrue() {
        String email = "email";
        String password = "password";
        when(userRepository.findByEmailIgnoreCase(email)).thenReturn(Optional.of(user));
        when(passwordUtil.isEqual(password, user.getPassword())).thenReturn(true);

        boolean authenticated = userService.authenticateUser(email, password);

        assertTrue(authenticated);
    }

    @DisplayName("Test for requestPasswordReset()")
    @Test
    public void testRequestPasswordReset() {
        RequestResetDto requestResetDto = new RequestResetDto("email");
        when(userRepository.findByEmailIgnoreCase(requestResetDto.getEmail()))
            .thenReturn(Optional.of(user));

        userService.requestPasswordReset(requestResetDto);

        verify(emailService).sendPasswordResetEmail(
            eq(requestResetDto.getEmail()),
            any(String.class)
        );
    }

    @DisplayName("Test for resetPassword()")
    @Test
    public void testResetPassword() {
        PasswordResetDto passwordResetDto = new PasswordResetDto("token", "new password");
        when(confirmationTokenRepository.findByConfirmationToken(passwordResetDto.getToken()))
            .thenReturn(Optional.of(new ConfirmationToken(unverifiedUser)));

        long userId = unverifiedUser.getUserId();
        when(userRepository.findById(userId))
            .thenReturn(Optional.of(unverifiedUser));

        when(passwordUtil.hashPassword(passwordResetDto.getPassword()))
            .thenReturn(passwordResetDto.getPassword());

        User result = userService.resetPassword(passwordResetDto);

        verify(userRepository).save(unverifiedUser);
        assertTrue(result.isVerified());
        assertEquals(result.getPassword(), passwordResetDto.getPassword());
    }

    @DisplayName("Test for resetPassword() with invalid token")
    @Test
    public void testResetPasswordThrowsInvalidTokenException() {
        PasswordResetDto passwordResetDto = new PasswordResetDto("token", "new password");
        when(confirmationTokenRepository.findByConfirmationToken(passwordResetDto.getToken()))
            .thenReturn(Optional.empty());

        assertThrows(InvalidTokenException.class, () -> userService.resetPassword(passwordResetDto));
    }

    @DisplayName("Test for resetPassword() with invalid user")
    @Test
    public void testResetPasswordThrowsNoSuchUserIdException() {
        PasswordResetDto passwordResetDto = new PasswordResetDto("token", "new password");
        when(confirmationTokenRepository.findByConfirmationToken(passwordResetDto.getToken()))
            .thenReturn(Optional.of(new ConfirmationToken(unverifiedUser)));

        when(userRepository.findById(unverifiedUser.getUserId()))
            .thenReturn(Optional.empty());

        assertThrows(NoSuchUserIdException.class, () -> userService.resetPassword(passwordResetDto));
    }

    @DisplayName("Test for findUserById()")
    @Test
    public void testFindUserByIdReturnsUserEntity() {
        final long id = 1;
        when(userRepository.findById(id)).thenReturn(Optional.of(user));
        user.setVerified(true);

        User foundUser = userService.findUserById(id);
        assertNotNull(foundUser);
    }

    @DisplayName("Test for findUserById() with invalid id")
    @Test
    public void testFindUserByIdThrowsNoSuchEmailException() {
        final long id = 1;
        when(userRepository.findById(id)).thenReturn(Optional.empty());

        assertThrows(NoSuchUserIdException.class, () -> userService.findUserById(id));
    }

    @DisplayName("Test for findUserById() with unverified user")
    @Test
    public void testFindUserByIdThrowsUnverifiedUserException() {
        final long id = 1;
        when(userRepository.findById(id)).thenReturn(Optional.of(unverifiedUser));

        assertThrows(UnverifiedUserException.class, () -> userService.findUserById(id));
    }

    @DisplayName("Test for findUserByEmail()")
    @Test
    public void testFindUserByEmailReturnsUserEntity() {
        String email = "email";
        when(userRepository.findByEmailIgnoreCase(email)).thenReturn(Optional.of(user));
        user.setVerified(true);

        User foundUser = userService.findUserByEmail(email);
        assertNotNull(foundUser);
    }

    @DisplayName("Test for findUserByEmail() with invalid email")
    @Test
    public void testFindUserByEmailThrowsNoSuchEmailException() {
        String invalidEmail = "invalid email";
        when(userRepository.findByEmailIgnoreCase(invalidEmail)).thenReturn(Optional.empty());

        assertThrows(NoSuchEmailException.class, () -> userService.findUserByEmail(invalidEmail));
    }

    @DisplayName("Test for findUserByEmail() with unverified user")
    @Test
    public void testFindUserByEmailThrowsUnverifiedUserException() {
        String email = "email";
        when(userRepository.findByEmailIgnoreCase(email)).thenReturn(Optional.of(unverifiedUser));

        assertThrows(UnverifiedUserException.class, () -> userService.findUserByEmail(email));
    }

    @DisplayName("Test for resendConfirmEmail doesnt work with verified user")
    @Test
    public void testResendConfirmEmailThrowsEmailAlreadyVerifiedException() {
        when(userRepository.findById(anyLong())).thenReturn(Optional.of(user));
        assertThrows(EmailAlreadyVerifiedException.class, () -> userService.resendConfirmEmail(VERIFIED_USER_ID));
    }

    @DisplayName("Test for resendConfirmEmail with too often requests")
    @Test
    public void testResendConfirmEmailThrowsTooOftenRequestedException() {
        when(userRepository.findById(anyLong())).thenReturn(Optional.of(unverifiedUser));
        ConfirmationToken confirmationToken = new ConfirmationToken(unverifiedUser);
        when(confirmationTokenRepository.findConfirmationTokenByUser(any())).thenReturn(Optional.of(confirmationToken));

        assertThrows(TooOftenRequestedException.class, () -> userService.resendConfirmEmail(UNVERIFIED_USER_ID));
    }


    @DisplayName("Test for resendConfirmEmail generates activation token and sends email")
    @Test
    public void testResendConfirmCreatesToken() {
        String generatedToken = "test_token";
        ConfirmationToken expectedToken = spy(new ConfirmationToken(unverifiedUser));
        when(userRepository.findById(anyLong())).thenReturn(Optional.of(unverifiedUser));
        when(confirmationTokenRepository.findConfirmationTokenByUser(any())).thenReturn(Optional.empty());
        when(userService.createConfirmationToken(any())).thenReturn(expectedToken);
        when(expectedToken.getConfirmationToken()).thenReturn(generatedToken);

        userService.resendConfirmEmail(UNVERIFIED_USER_ID);

        verify(userRepository).findById(eq(UNVERIFIED_USER_ID));
        verify(confirmationTokenRepository).findConfirmationTokenByUser(eq(unverifiedUser));
        verify(confirmationTokenRepository).save(eq(expectedToken));
        verify(emailService).sendConfirmationEmail(eq(unverifiedUser.getEmail()), eq(generatedToken));
    }

    @DisplayName("Test for resendConfirmEmail deletes existing token")
    @Test
    public void testResendConfirmEmailDeletesToken() {
        when(userRepository.findById(anyLong())).thenReturn(Optional.of(unverifiedUser));
        ConfirmationToken confirmationToken = new ConfirmationToken(unverifiedUser);
        confirmationToken.setCreatedDate(OffsetDateTime.now().minusHours(1L));
        when(confirmationTokenRepository.findConfirmationTokenByUser(any())).thenReturn(Optional.of(confirmationToken));
        when(confirmationTokenRepository.save(any())).thenReturn(new ConfirmationToken());
        doNothing().when(emailService).sendConfirmationEmail(anyString(), anyString());

        userService.resendConfirmEmail(UNVERIFIED_USER_ID);

        verify(confirmationTokenRepository).deleteByTokenId(confirmationToken.getTokenId());
    }
}
