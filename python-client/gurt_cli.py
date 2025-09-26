#!/usr/bin/env python3
"""
GURT CLI Tool

A command-line tool for making requests to GURT servers.
"""

import argparse
import sys
import json
import logging
from typing import Optional

from gurt import GurtClient, GurtClientConfig, GurtError


def setup_logging(verbose: bool):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def print_response(response, show_headers: bool = False, format_json: bool = False):
    """Print response in a formatted way"""
    print(f"Status: {response.status_code} {response.status_message}")
    
    if show_headers:
        print("\nHeaders:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
    
    if response.body:
        print("\nBody:")
        try:
            if format_json and response.get_header('content-type') == 'application/json':
                data = response.json()
                print(json.dumps(data, indent=2))
            else:
                print(response.text())
        except Exception as e:
            print(f"<Binary data or encoding error: {e}>")


def cmd_get(args):
    """Handle GET command"""
    config = GurtClientConfig(
        verify_tls=not args.insecure,
        request_timeout=args.timeout
    )
    client = GurtClient(config)
    
    try:
        response = client.get(args.url)
        print_response(response, args.headers, args.json)
    except GurtError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


def cmd_post(args):
    """Handle POST command"""
    config = GurtClientConfig(
        verify_tls=not args.insecure,
        request_timeout=args.timeout
    )
    client = GurtClient(config)
    
    # Prepare body
    body = ""
    content_type = "text/plain"
    
    if args.json_data:
        body = json.dumps(args.json_data)
        content_type = "application/json"
    elif args.data:
        body = args.data
        content_type = args.content_type or "text/plain"
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                body = f.read()
            content_type = args.content_type or "text/plain"
        except IOError as e:
            print(f"Error reading file {args.file}: {e}", file=sys.stderr)
            return 1
    
    try:
        response = client.post(args.url, body, content_type)
        print_response(response, args.headers, args.json)
    except GurtError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


def cmd_put(args):
    """Handle PUT command"""
    config = GurtClientConfig(
        verify_tls=not args.insecure,
        request_timeout=args.timeout
    )
    client = GurtClient(config)
    
    # Prepare body
    body = ""
    content_type = "text/plain"
    
    if args.json_data:
        body = json.dumps(args.json_data)
        content_type = "application/json"
    elif args.data:
        body = args.data
        content_type = args.content_type or "text/plain"
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                body = f.read()
            content_type = args.content_type or "text/plain"
        except IOError as e:
            print(f"Error reading file {args.file}: {e}", file=sys.stderr)
            return 1
    
    try:
        response = client.put(args.url, body, content_type)
        print_response(response, args.headers, args.json)
    except GurtError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


def cmd_delete(args):
    """Handle DELETE command"""
    config = GurtClientConfig(
        verify_tls=not args.insecure,
        request_timeout=args.timeout
    )
    client = GurtClient(config)
    
    try:
        response = client.delete(args.url)
        print_response(response, args.headers, args.json)
    except GurtError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


def cmd_head(args):
    """Handle HEAD command"""
    config = GurtClientConfig(
        verify_tls=not args.insecure,
        request_timeout=args.timeout
    )
    client = GurtClient(config)
    
    try:
        response = client.head(args.url)
        print_response(response, True, args.json)  # Always show headers for HEAD
    except GurtError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="GURT Protocol Client - Connect to Gurted network"
    )
    
    # Global options
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Enable verbose logging")
    parser.add_argument("--insecure", action="store_true",
                       help="Disable TLS certificate verification")
    parser.add_argument("--timeout", type=float, default=30.0,
                       help="Request timeout in seconds (default: 30)")
    parser.add_argument("--headers", action="store_true",
                       help="Show response headers")
    parser.add_argument("--json", action="store_true",
                       help="Format JSON responses")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # GET command
    get_parser = subparsers.add_parser("get", help="Send a GET request")
    get_parser.add_argument("url", help="GURT URL to request")
    get_parser.set_defaults(func=cmd_get)
    
    # POST command
    post_parser = subparsers.add_parser("post", help="Send a POST request")
    post_parser.add_argument("url", help="GURT URL to request")
    post_parser.add_argument("-d", "--data", help="Request body data")
    post_parser.add_argument("-j", "--json_data", type=json.loads, 
                            help="JSON data (will be serialized)")
    post_parser.add_argument("-f", "--file", help="Read body from file")
    post_parser.add_argument("-t", "--content-type", 
                            help="Content-Type header")
    post_parser.set_defaults(func=cmd_post)
    
    # PUT command  
    put_parser = subparsers.add_parser("put", help="Send a PUT request")
    put_parser.add_argument("url", help="GURT URL to request")
    put_parser.add_argument("-d", "--data", help="Request body data")
    put_parser.add_argument("-j", "--json_data", type=json.loads,
                           help="JSON data (will be serialized)")
    put_parser.add_argument("-f", "--file", help="Read body from file")
    put_parser.add_argument("-t", "--content-type",
                           help="Content-Type header")
    put_parser.set_defaults(func=cmd_put)
    
    # DELETE command
    delete_parser = subparsers.add_parser("delete", help="Send a DELETE request")
    delete_parser.add_argument("url", help="GURT URL to request")
    delete_parser.set_defaults(func=cmd_delete)
    
    # HEAD command
    head_parser = subparsers.add_parser("head", help="Send a HEAD request")
    head_parser.add_argument("url", help="GURT URL to request")
    head_parser.set_defaults(func=cmd_head)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())