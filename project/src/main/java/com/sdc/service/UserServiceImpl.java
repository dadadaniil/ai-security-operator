package com.sdc.service;

import com.sdc.controller.exception.custom.*;
import com.sdc.model.ConfirmationToken;
import com.sdc.model.User;
import com.sdc.model.dto.PasswordResetDto;
import com.sdc.model.dto.RequestResetDto;
import com.sdc.model.dto.UserDto;
import com.sdc.repository.ConfirmationTokenRepository;
import com.sdc.repository.RoleRepository;
import com.sdc.repository.UserRepository;
import com.sdc.util.PasswordUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.OffsetDateTime;
import java.util.Optional;

@Service
public class UserServiceImpl implements UserService {
    private static final Logger logger = LoggerFactory.getLogger(UserService.class);
    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final ConfirmationTokenRepository confirmationTokenRepository;
    private final ConfirmationTokenService confirmationTokenService;
    private final EmailService emailService;
    private final PasswordUtil passwordUtil;

    public UserServiceImpl(
        UserRepository userRepository,
        RoleRepository roleRepository,
        ConfirmationTokenRepository confirmationTokenRepository,
        EmailService emailService,
        PasswordUtil passwordUtil,
        ConfirmationTokenService confirmationTokenService
    ) {
        this.userRepository = userRepository;
        this.roleRepository = roleRepository;
        this.confirmationTokenRepository = confirmationTokenRepository;
        this.emailService = emailService;
        this.passwordUtil = passwordUtil;
        this.confirmationTokenService= confirmationTokenService;
    }

    public User saveUser(UserDto user) {
        if (userRepository.existsByEmail(user.getEmail())) {
            throw EmailInUseException.createWith(user.getEmail());
        }

        User newUser = new User(user.getFirstName(), user.getLastName(), user.getEmail(), passwordUtil.hashPassword(user.getPassword()));
        newUser.setRole(roleRepository.getReferenceById(user.getRoleId()));

        userRepository.save(newUser);

        ConfirmationToken confirmationToken = createConfirmationToken(newUser);
        confirmationTokenRepository.save(confirmationToken);

        emailService.sendConfirmationEmail(user.getEmail(), confirmationToken.getConfirmationToken());
        logger.info("Confirmation Token: {}", confirmationToken.getConfirmationToken());

        return newUser;
    }

    @Override
    public void confirmEmail(String confirmationToken) {
        Optional<ConfirmationToken> tokenOptional = confirmationTokenRepository.findByConfirmationToken(confirmationToken);

        if (tokenOptional.isEmpty()) {
            throw new InvalidTokenException();
        }

        ConfirmationToken token = tokenOptional.get();
        if (confirmationTokenService.isExpired(token)) {
            confirmationTokenRepository.deleteByTokenId(token.getTokenId());
            throw ExpiredTokenException.createWith(token.getConfirmationToken());
        }

        Optional<User> userOptional = userRepository.findById(token.getUser().getUserId());
        if (userOptional.isEmpty()) {
            throw NoSuchUserIdException.createWith(token.getUser().getUserId());
        }

        User user = userOptional.get();
        user.setVerified(true);
        confirmationTokenRepository.deleteByTokenId(token.getTokenId());
        userRepository.save(user);
    }

    @Override
    public void resendConfirmEmail(Long userId) {
        Optional<User> userOptional = userRepository.findById(userId);
        if (userOptional.isEmpty()) {
            throw NoSuchUserIdException.createWith(userId);
        }

        User user = userOptional.get();
        if (user.isVerified()) {
            throw EmailAlreadyVerifiedException.createWith(userId);
        }

        Optional<ConfirmationToken> tokenOptional = confirmationTokenRepository.findConfirmationTokenByUser(user);
        if (tokenOptional.isPresent()) {
            if (tokenOptional.get().getCreatedDate().isAfter(OffsetDateTime.now().minusMinutes(3))) {
                throw new TooOftenRequestedException();
            }
            confirmationTokenRepository.deleteByTokenId(tokenOptional.get().getTokenId());
        }

        ConfirmationToken confirmationToken = createConfirmationToken(user);
        confirmationTokenRepository.save(confirmationToken);
        emailService.sendConfirmationEmail(user.getEmail(), confirmationToken.getConfirmationToken());
        logger.info("Confirmation Token: {}", confirmationToken.getConfirmationToken());
    }

    @Override
    public boolean authenticateUser(String email, String password) {
        User user = findUserByEmail(email);
        return passwordUtil.isEqual(password, user.getPassword());
    }

    public void requestPasswordReset(RequestResetDto requestResetDto) {
        String email = requestResetDto.getEmail();

        User user = findUserByEmail(email);

        confirmationTokenRepository.deleteConfirmationTokensByUser(user);
        ConfirmationToken confirmationToken = createConfirmationToken(user);
        confirmationTokenRepository.save(confirmationToken);

        user.setVerified(false);

        userRepository.save(user);
        emailService.sendPasswordResetEmail(email, confirmationToken.getConfirmationToken());
    }

    @Override
    public User resetPassword(PasswordResetDto passwordResetDto) {
        String password = passwordResetDto.getPassword();

        Optional<ConfirmationToken> tokenOptional = confirmationTokenRepository.findByConfirmationToken(passwordResetDto.getToken());
        if (tokenOptional.isEmpty()) {
            throw new InvalidTokenException();
        }

        ConfirmationToken token = tokenOptional.get();
        if (confirmationTokenService.isExpired(token)) {
            confirmationTokenRepository.deleteByTokenId(token.getTokenId());
            throw ExpiredTokenException.createWith(token.getConfirmationToken());
        }

        long userId = token.getUser().getUserId();
        Optional<User> userOptional = userRepository.findById(userId);
        if (userOptional.isEmpty()) {
            throw NoSuchUserIdException.createWith(userId);
        }

        User user = userOptional.get();
        user.setVerified(true);
        user.setPassword(passwordUtil.hashPassword(password));
        userRepository.save(user);
        confirmationTokenRepository.deleteByTokenId(token.getTokenId());
        return user;
    }

    @Override
    public User findUserById(long id) {
        Optional<User> userOptional = userRepository.findById(id);
        if (userOptional.isEmpty()) {
            throw NoSuchUserIdException.createWith(id);
        }

        User user = userOptional.get();
        if (!user.isVerified()) {
            throw UnverifiedUserException.createWith(user.getUserId());
        }

        return user;
    }

    @Override
    public User findUserByEmail(String email) {
        Optional<User> userOptional = userRepository.findByEmailIgnoreCase(email);
        if (userOptional.isEmpty()) {
            throw NoSuchEmailException.createWith(email);
        }

        User user = userOptional.get();
        if (!user.isVerified()) {
            throw UnverifiedUserException.createWith(user.getUserId());
        }

        return user;
    }

    ConfirmationToken createConfirmationToken(User user) {
        return new ConfirmationToken(user);
    }
}
