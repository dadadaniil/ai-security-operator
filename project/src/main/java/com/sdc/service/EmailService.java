package com.sdc.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Service
public class EmailService {

    private final JavaMailSender javaMailSender;

    private final String baseUrl;

    @Autowired
    public EmailService(
        JavaMailSender javaMailSender,
        @Value("${application.ui.url}") String baseUrl
    ) {
        this.baseUrl = baseUrl;
        this.javaMailSender = javaMailSender;
    }

    @Async
    public void sendConfirmationEmail(String email, String confirmationToken) {
        SimpleMailMessage mailMessage = new SimpleMailMessage();
        mailMessage.setTo(email);
        mailMessage.setSubject("Complete Registration!");
        mailMessage.setText("To confirm your account, please follow the link : "
            + baseUrl + "/api/users/confirm-account?token=" + confirmationToken);

        javaMailSender.send(mailMessage);
    }

    @Async
    public void sendPasswordResetEmail(String email, String token) {
        SimpleMailMessage mailMessage = new SimpleMailMessage();
        mailMessage.setTo(email);
        mailMessage.setSubject("Password Reset Request");
        mailMessage.setText("To reset your password, please click here : "
            + baseUrl + "/api/users/password-reset?token=" + token);

        javaMailSender.send(mailMessage);
    }
}
