from burp import IBurpExtender, IContextMenuFactory
from java.util import List, ArrayList
from javax.swing import JMenuItem
import java.awt.datatransfer.StringSelection as StringSelection
import java.awt.Toolkit as Toolkit
from urlparse import urlparse

class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        # Set the name of the extension
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self._callbacks.setExtensionName("Copy Subdirectory Paths Only")

        # Register the extension as a context menu factory
        callbacks.registerContextMenuFactory(self)
    
    def createMenuItems(self, invocation):
        menu = ArrayList()
        menuItem = JMenuItem("Copy Subdirectory Paths Only", actionPerformed=lambda x: self.copySubdirectoryPaths(invocation))
        menu.add(menuItem)
        return menu

    def copySubdirectoryPaths(self, invocation):
        selectedItems = invocation.getSelectedMessages()

        if selectedItems:
            # Get the first selected request to determine the base path
            first_item = selectedItems[0]
            requestInfo = self._helpers.analyzeRequest(first_item)
            selected_url = requestInfo.getUrl()
            selected_path = urlparse(str(selected_url)).path
            
            # Ensure the base path ends with a slash for consistency (e.g., '/admin/')
            if not selected_path.endswith('/'):
                selected_path += '/'

            # Get the site map from Burp's current project
            sitemap_items = self._callbacks.getSiteMap(None)
            
            # Store unique paths that match the selected base path
            matching_paths = set()

            # Iterate over the site map and find paths that start with the selected subdirectory
            for item in sitemap_items:
                url = item.getUrl()
                
                # Check if the host matches the selected one
                if url.getHost() == selected_url.getHost():
                    parsed_url = urlparse(str(url))
                    full_path = parsed_url.path

                    # Only replace leading double slashes (//) with a single slash (/)
                    if full_path.startswith('//'):
                        clean_path = '/' + full_path[2:]  # Replace only the leading double slash
                    else:
                        clean_path = full_path

                    # Add the path if it starts with the selected base path (e.g., '/admin/')
                    if clean_path.startswith(selected_path):
                        matching_paths.add(clean_path)

            # Copy all matching paths to the clipboard
            clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
            clipboard.setContents(StringSelection("\n".join(sorted(set(matching_paths)))), None)
