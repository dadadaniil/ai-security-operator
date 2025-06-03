package com.sdc.service.mapper;

import com.sdc.model.User;
import com.sdc.model.dto.UserViewDto;
import org.springframework.stereotype.Component;

@Component
public class UserToCreatorMapper {
    public UserViewDto userToUserViewDto(User user) {
        UserViewDto userViewDto = new UserViewDto();
        userViewDto.setId(user.getUserId());
        userViewDto.setFirstName(user.getFirstName());
        userViewDto.setLastName(user.getLastName());
        userViewDto.setEmail(user.getEmail());
        return userViewDto;
    }
}