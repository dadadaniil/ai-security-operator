package com.sdc.controller.web;

import com.sdc.controller.configuration.auth.JwtService;
import com.sdc.model.dto.GenericResponse;
import com.sdc.model.dto.PageDto;
import com.sdc.model.dto.TagDto;
import com.sdc.service.TagService;
import com.sdc.util.Constants;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.*;

import static org.springframework.http.HttpStatus.OK;

@RestController
@RequestMapping("/api/tags")
public class TagController {
    private final TagService service;

    public TagController(TagService service, JwtService ignoredJwtService) {
        this.service = service;
    }

    @GetMapping
    @ResponseStatus(OK)
    public GenericResponse<PageDto<TagDto>> getAllTags(
        @RequestParam(defaultValue = "1") int pageNum,
        @RequestParam(defaultValue = Constants.DEFAULT_TAG_PAGE_SIZE) int pageSize
    ) {
        final PageRequest pageRequest = PageRequest.of(pageNum - 1, pageSize);
        final PageDto<TagDto> tags = service.findAll(pageRequest);
        return GenericResponse.success(OK, tags);
    }

    @GetMapping("/{id}")
    @ResponseStatus(OK)
    public GenericResponse<TagDto> getTagById(@PathVariable("id") Long id) {
        return GenericResponse.success(OK, service.findTagById(id));
    }
}
