require('dotenv').config();
const express = require('express');
const { App } = require('@octokit/app');
const { Webhooks, createNodeMiddleware } = require('@octokit/webhooks');
const axios = require('axios');

const GITHUB_APP_ID = process.env.GITHUB_APP_ID;
const GITHUB_PRIVATE_KEY = process.env.GITHUB_PRIVATE_KEY.replace(/\\n/g, '\n');
const GITHUB_WEBHOOK_SECRET = process.env.GITHUB_WEBHOOK_SECRET;
const GITHUB_INSTALLATION_ID = process.env.GITHUB_INSTALLATION_ID;
const COMMAND_PREFIX = process.env.COMMAND_PREFIX || '!run-check';
const EXTERNAL_SERVICE_URL = process.env.EXTERNAL_SERVICE_URL;
const PORT = process.env.PORT || 3000;

if (!GITHUB_APP_ID || !GITHUB_PRIVATE_KEY || !GITHUB_WEBHOOK_SECRET || !GITHUB_INSTALLATION_ID || !EXTERNAL_SERVICE_URL) {
    console.error('Missing one or more required environment variables. Please check your configuration.');
    process.exit(1);
}

const app = express();


const ghApp = new App({
    appId: parseInt(GITHUB_APP_ID, 10),
    privateKey: GITHUB_PRIVATE_KEY,
});


const webhooks = new Webhooks({
    secret: GITHUB_WEBHOOK_SECRET,
});


class PRBot {
    constructor(octokit) {
        this.octokit = octokit;
    }

    async handleComment(payload) {
        console.log('Received issue_comment event');

        if (!payload.issue.pull_request) {
            console.log('Comment is not on a pull request. Ignoring.');
            return;
        }

        const commentBody = payload.comment.body;
        if (!commentBody.startsWith(COMMAND_PREFIX)) {
            console.log(`Comment does not start with command prefix "${COMMAND_PREFIX}". Ignoring.`);
            return;
        }

        const parts = commentBody.substring(COMMAND_PREFIX.length).trim().split(/\s+/);
        const command = parts[0];
        const args = parts.slice(1).join(' ');

        console.log(`Parsed command: "${command}", Args: "${args}"`);

        try {
            console.log(`Calling external service at ${EXTERNAL_SERVICE_URL} with command: ${command}`);
            const serviceResponse = await axios.post(EXTERNAL_SERVICE_URL, {
                command: command,
                args: args,
            });



            const responseMessage = serviceResponse.data && serviceResponse.data.message
                ? serviceResponse.data.message
                : 'External service processed the command.';

            console.log('External service responded. Posting comment to PR.');
            await this.postCommentToPR(payload, responseMessage);

        } catch (error) {
            console.error('Error calling external service or processing its response:', error.message);
            let errorMessage = 'Error: Could not process command.';
            if (error.response) {
                errorMessage += ` External service responded with status ${error.response.status}.`;
                console.error('External service error details:', error.response.data);
            } else if (error.request) {
                errorMessage += ' Failed to reach external service.';
            } else {
                errorMessage += ` ${error.message}`;
            }
            await this.postCommentToPR(payload, errorMessage);
        }
    }

    async postCommentToPR(originalPayload, message) {
        const owner = originalPayload.repository.owner.login;
        const repo = originalPayload.repository.name;
        const issue_number = originalPayload.issue.number;

        try {
            await this.octokit.request('POST /repos/{owner}/{repo}/issues/{issue_number}/comments', {
                owner,
                repo,
                issue_number,
                body: message,
                headers: {
                    'x-github-api-version': '2022-11-28'
                }
            });
            console.log(`Successfully posted comment to PR #${issue_number}`);
        } catch (error) {
            console.error(`Failed to post comment to PR #${issue_number}:`, error.message);
        }
    }
}


webhooks.on('issue_comment.created', async ({ id, name, payload }) => {
    console.log(`Webhook event received: ${name} (id: ${id})`);
    try {
        const installationIdAsNumber = parseInt(GITHUB_INSTALLATION_ID, 10);
        if (isNaN(installationIdAsNumber)) {
            console.error('Invalid GITHUB_INSTALLATION_ID: Not a number. Please check your configuration.');
            return;
        }
        const octokit = await ghApp.getInstallationOctokit(installationIdAsNumber);
        const bot = new PRBot(octokit);
        await bot.handleComment(payload);
    } catch (error) {
        console.error('Error processing webhook event:', error.message);
        if (error.status === 401 && error.message.includes('found an installation id')) {
            console.error('Ensure your GITHUB_INSTALLATION_ID is correct and the GitHub App is installed on the repository.');
        }
    }
});



app.use('/webhook', createNodeMiddleware(webhooks, { path: '/webhook' }));


app.use((err, req, res, next) => {
    if (err instanceof Webhooks.errors.EventError || err instanceof Webhooks.errors.SignatureVerificationError) {
        console.error(`Webhook Error: ${err.message}`);
        res.status(err.status || 500).send(err.message || 'Webhook processing error');
    } else {
        console.error('Unhandled application error:', err);
        res.status(500).send('Internal Server Error');
    }
});

app.get('/health', (req, res) => {
    res.status(200).send('OK');
});

app.listen(PORT, () => {
    console.log(`GitHub Bot server listening on port ${PORT}`);
    console.log('Ensure your GitHub App webhook is configured to point to /webhook at your exposed URL (e.g., via Smee.io for local dev).');
    console.log(`Using command prefix: "${COMMAND_PREFIX}"`);
    console.log(`External service URL: "${EXTERNAL_SERVICE_URL}"`);
});


process.on('SIGINT', () => {
    console.log('SIGINT signal received: closing HTTP server');

    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('SIGTERM signal received: closing HTTP server');

    process.exit(0);
}); 